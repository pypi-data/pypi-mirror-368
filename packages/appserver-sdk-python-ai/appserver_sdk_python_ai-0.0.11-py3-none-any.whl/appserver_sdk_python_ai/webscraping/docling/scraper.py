# appserver_sdk_python_ai/webscraping/docling/scraper.py
"""
WebDocling - Scraper principal com Docling
==========================================

Classe principal para web scraping usando Docling para conversão de alta qualidade.
Integrado à biblioteca appserver_sdk_python_ai.
"""

import logging
import os
import re
import tempfile
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise ImportError(
        "BeautifulSoup4 não está instalado. Execute: pip install beautifulsoup4 lxml"
    ) from None

try:
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PipelineOptions
    from docling.document_converter import DocumentConverter

    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    logging.warning("Docling não está disponível. Usando conversão básica.")

from ..core.config import ScrapingConfig
from ..core.exceptions import (
    ConversionError,
    NetworkError,
    WebScrapingError,
)
from ..core.models import ScrapingResult
from ..utils.cache import CacheManager
from ..utils.cleaner import ContentCleaner
from ..utils.validators import URLValidator

__version__ = "1.0.0"


class DoclingWebScraper:
    """Classe principal para web scraping com Docling."""

    def __init__(self, config: ScrapingConfig | None = None):
        """
        Inicializa o scraper.

        Args:
            config: Configurações de scraping. Se None, usa configuração padrão.
        """
        self.config = config or ScrapingConfig()
        self.session = requests.Session()
        self.cache_manager = CacheManager() if self.config.enable_cache else None

        # Configurar logging primeiro
        self.logger = logging.getLogger(__name__)

        # Configurar sessão
        self.session.headers.update(self.config.get_headers())
        if self.config.cookies:
            self.session.cookies.update(self.config.cookies)

        # Inicializar Docling se disponível
        self._initialize_docling()

    def _initialize_docling(self):
        """Inicializa o conversor Docling."""
        if not DOCLING_AVAILABLE:
            self.docling_converter = None
            return

        try:
            pipeline_options = PipelineOptions()
            pipeline_options.do_ocr = False
            pipeline_options.do_table_structure = True

            self.docling_converter = DocumentConverter(
                allowed_formats=[InputFormat.HTML], pipeline_options=pipeline_options
            )
        except Exception as e:
            self.logger.warning(f"Erro ao inicializar Docling: {e}")
            self.docling_converter = None

    def scrape_to_markdown(
        self, url: str, output_file: str | None = None
    ) -> ScrapingResult:
        """
        Faz scraping de uma URL e converte para markdown.

        Args:
            url: URL para fazer scraping
            output_file: Caminho opcional para salvar o arquivo

        Returns:
            ScrapingResult: Resultado da operação
        """
        start_time = time.time()

        try:
            # Validar URL
            URLValidator.validate_url(url)

            # Fazer download do conteúdo
            html_content = self._download_content(url)

            # Limpar HTML
            if self.config.clean_html:
                html_content = ContentCleaner.clean_html(html_content, url, self.config)

            # Converter para markdown
            markdown_content, title, metadata = self._convert_to_markdown(
                html_content, url
            )

            # Salvar arquivo se especificado
            if output_file:
                self._save_file(markdown_content, output_file)

            processing_time = time.time() - start_time

            return ScrapingResult(
                url=url,
                title=title,
                content=markdown_content,
                metadata=metadata,
                success=True,
                processing_time=processing_time,
                content_length=len(markdown_content),
            )

        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = str(e)
            self.logger.error(f"Erro no scraping de {url}: {error_msg}")

            return ScrapingResult(
                url=url,
                title="",
                content="",
                metadata={},
                success=False,
                error=error_msg,
                processing_time=processing_time,
            )

    def batch_scrape(
        self,
        urls: list[str],
        output_dir: str | None = None,
        max_workers: int = 5,
        progress_callback: Callable | None = None,
    ) -> list[ScrapingResult]:
        """
        Faz scraping de múltiplas URLs em paralelo.

        Args:
            urls: Lista de URLs
            output_dir: Diretório de saída (opcional)
            max_workers: Número máximo de threads
            progress_callback: Callback para acompanhar progresso

        Returns:
            List[ScrapingResult]: Lista de resultados
        """
        results = []

        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submeter todas as tarefas
            future_to_url = {}
            for url in urls:
                output_file = None
                if output_dir:
                    filename = self._generate_filename(url)
                    output_file = str(output_path / filename)

                future = executor.submit(self.scrape_to_markdown, url, output_file)
                future_to_url[future] = url

            # Processar resultados conforme completam
            completed = 0
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1

                    if progress_callback:
                        progress_callback(completed, len(urls), url, result.success)

                except Exception as e:
                    self.logger.error(f"Erro no processamento de {url}: {e}")
                    results.append(
                        ScrapingResult(
                            url=url,
                            title="",
                            content="",
                            metadata={},
                            success=False,
                            error=str(e),
                        )
                    )

        return results

    def _download_content(self, url: str) -> str:
        """Baixa conteúdo da URL com retry e cache."""
        headers = self.config.get_headers()

        # Tentar cache primeiro
        if self.cache_manager:
            cached_content = self.cache_manager.get(url, headers, self.config.cache_ttl)
            if cached_content:
                self.logger.info(f"Conteúdo obtido do cache: {url}")
                return cached_content

        # Fazer download com retry
        for attempt in range(self.config.retry_attempts):
            try:
                self.logger.info(f"Baixando conteúdo (tentativa {attempt + 1}): {url}")

                response = self.session.get(
                    url,
                    timeout=self.config.timeout,
                    allow_redirects=self.config.follow_redirects,
                    verify=self.config.verify_ssl,
                    stream=True,
                )
                response.raise_for_status()

                # Verificar tamanho do conteúdo
                content_length = response.headers.get("content-length")
                if (
                    content_length
                    and int(content_length) > self.config.max_content_length
                ):
                    raise NetworkError(f"Conteúdo muito grande: {content_length} bytes")

                # Detectar encoding
                encoding = self.config.encoding or response.encoding or "utf-8"
                response.encoding = encoding

                content = response.text

                # Verificar se é HTML
                content_type = response.headers.get("content-type", "").lower()
                if "html" not in content_type and "xml" not in content_type:
                    self.logger.warning(f"Tipo de conteúdo inesperado: {content_type}")

                # Armazenar no cache
                if self.cache_manager:
                    self.cache_manager.set(url, headers, content)

                self.logger.info(f"Download concluído: {len(content)} caracteres")
                return content

            except requests.RequestException as e:
                if attempt == self.config.retry_attempts - 1:
                    raise NetworkError(
                        f"Erro na requisição após {self.config.retry_attempts} tentativas: {e}"
                    ) from e

                self.logger.warning(f"Tentativa {attempt + 1} falhou: {e}")
                time.sleep(
                    self.config.retry_delay * (2**attempt)
                )  # Backoff exponencial

        # Se chegou aqui, todas as tentativas falharam
        raise NetworkError(f"Falha ao baixar conteúdo após {self.config.retry_attempts} tentativas")

    def _convert_to_markdown(self, html_content: str, source_url: str) -> tuple:
        """Converte HTML para markdown."""
        if self.docling_converter:
            return self._convert_with_docling(html_content, source_url)
        else:
            return self._convert_basic(html_content, source_url)

    def _convert_with_docling(self, html_content: str, source_url: str) -> tuple:
        """Converte usando Docling."""
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False, encoding="utf-8"
            ) as temp_file:
                temp_file.write(html_content)
                temp_file_path = temp_file.name

            try:
                self.logger.info("Convertendo com Docling...")
                result = self.docling_converter.convert(temp_file_path)
                markdown_content = result.document.export_to_markdown()

                # Extrair metadados
                title = self._extract_title(html_content)
                metadata = self._extract_metadata(html_content, source_url)

                # Adicionar cabeçalho com metadados
                header = self._generate_markdown_header(title, source_url, metadata)
                final_content = header + markdown_content

                return final_content, title, metadata

            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            self.logger.error(f"Erro na conversão com Docling: {e}")
            return self._convert_basic(html_content, source_url)

    def _convert_basic(self, html_content: str, source_url: str) -> tuple:
        """Conversão básica usando BeautifulSoup."""
        try:
            soup = BeautifulSoup(html_content, "lxml")

            title = self._extract_title(html_content)
            metadata = self._extract_metadata(html_content, source_url)

            # Extrair conteúdo principal
            main_content = (
                soup.find("main")
                or soup.find("article")
                or soup.find("div", class_=re.compile(r"content|main|body", re.I))
                or soup.find("body")
                or soup
            )

            markdown_lines = []

            # Processar elementos
            for element in main_content.find_all(  # type: ignore
                [
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                    "h6",
                    "p",
                    "ul",
                    "ol",
                    "blockquote",
                    "pre",
                    "table",
                ]
            ):
                if element.name.startswith("h"):
                    level = int(element.name[1])
                    text = element.get_text().strip()
                    if text:
                        markdown_lines.append(f"{'#' * level} {text}\n")

                elif element.name == "p":
                    text = element.get_text().strip()
                    if text:
                        markdown_lines.append(f"{text}\n")

                elif element.name in ["ul", "ol"]:
                    for li in element.find_all("li", recursive=False):
                        prefix = "- " if element.name == "ul" else "1. "
                        text = li.get_text().strip()
                        if text:
                            markdown_lines.append(f"{prefix}{text}\n")

                elif element.name == "blockquote":
                    text = element.get_text().strip()
                    if text:
                        lines = text.split("\n")
                        for line in lines:
                            if line.strip():
                                markdown_lines.append(f"> {line.strip()}\n")

                elif element.name == "pre":
                    text = element.get_text()
                    markdown_lines.append(f"```\n{text}\n```\n")

                elif element.name == "table":
                    markdown_lines.append(self._convert_table_to_markdown(element))

            content = "\n".join(markdown_lines)
            header = self._generate_markdown_header(title, source_url, metadata)
            final_content = header + content

            return final_content, title, metadata

        except Exception as e:
            self.logger.error(f"Erro na conversão básica: {e}")
            raise ConversionError(f"Falha na conversão: {e}") from e

    def _extract_title(self, html_content: str) -> str:
        """Extrai título da página."""
        try:
            soup = BeautifulSoup(html_content, "lxml")

            # Tentar diferentes fontes para o título
            title_sources = [
                soup.find("title"),
                soup.find("h1"),
                soup.find("meta", property="og:title"),
                soup.find("meta", attrs={"name": "twitter:title"}),
            ]

            for source in title_sources:
                if source:
                    if hasattr(source, 'name') and source.name == "meta":  # type: ignore
                        title = source.get("content", "").strip()  # type: ignore
                    else:
                        title = source.get_text().strip()  # type: ignore

                    if title:
                        return title  # type: ignore

            return "Conteúdo Extraído"

        except Exception:
            return "Conteúdo Extraído"

    def _extract_metadata(self, html_content: str, source_url: str) -> dict[str, Any]:
        """Extrai metadados da página."""
        try:
            soup = BeautifulSoup(html_content, "lxml")
            metadata = {
                "source_url": source_url,
                "extracted_at": datetime.now().isoformat(),
                "converter": "Docling" if self.docling_converter else "Basic",
                "version": __version__,
            }

            # Meta tags
            meta_mappings = {
                "description": ["description", "og:description", "twitter:description"],
                "author": ["author", "og:author"],
                "keywords": ["keywords"],
                "language": ["language", "og:locale"],
                "published": ["article:published_time", "datePublished"],
                "modified": ["article:modified_time", "dateModified"],
            }

            for key, meta_names in meta_mappings.items():
                for meta_name in meta_names:
                    meta_tag = soup.find(
                        "meta", attrs={"name": meta_name}
                    ) or soup.find("meta", attrs={"property": meta_name})  # type: ignore
                    if meta_tag and meta_tag.get("content"):  # type: ignore
                        metadata[key] = meta_tag["content"].strip()  # type: ignore
                        break

            # Estatísticas do conteúdo
            text_content = soup.get_text()
            metadata["word_count"] = str(len(text_content.split()))
            metadata["char_count"] = str(len(text_content))

            return metadata

        except Exception as e:
            self.logger.warning(f"Erro ao extrair metadados: {e}")
            return {
                "source_url": source_url,
                "extracted_at": datetime.now().isoformat(),
                "converter": "Docling" if self.docling_converter else "Basic",
                "version": __version__,
            }

    def _generate_markdown_header(
        self, title: str, source_url: str, metadata: dict[str, Any]
    ) -> str:
        """Gera cabeçalho markdown com metadados."""
        header_lines = [
            "---",
            f'title: "{title}"',
            f"source: {source_url}",
            f"extracted_at: {metadata.get('extracted_at', '')}",
            f"converter: {metadata.get('converter', 'Basic')}",
            f"version: {metadata.get('version', __version__)}",
        ]

        # Adicionar outros metadados se disponíveis
        for key, value in metadata.items():
            if (
                key not in ["source_url", "extracted_at", "converter", "version"]
                and value
            ):
                header_lines.append(f'{key}: "{value}"')

        header_lines.extend(["---", "", f"# {title}", ""])

        return "\n".join(header_lines)

    def _convert_table_to_markdown(self, table_element) -> str:
        """Converte tabela HTML para markdown."""
        try:
            rows = []

            # Processar linhas
            for row in table_element.find_all("tr"):
                cells = []
                for cell in row.find_all(["td", "th"]):
                    text = cell.get_text().strip().replace("\n", " ")
                    cells.append(text)

                if cells:
                    rows.append(f"| {' | '.join(cells)} |")

            if not rows:
                return ""

            # Adicionar linha de separação após cabeçalho se houver th
            if table_element.find("th"):
                header_row = rows[0]
                num_cols = header_row.count("|") - 1
                separator = f"| {' | '.join(['---'] * num_cols)} |"
                rows.insert(1, separator)

            return "\n".join(rows) + "\n\n"

        except Exception as e:
            self.logger.warning(f"Erro ao converter tabela: {e}")
            return ""

    def _generate_filename(self, url: str) -> str:
        """Gera nome de arquivo baseado na URL."""
        parsed = urlparse(url)
        filename = f"{parsed.netloc}{parsed.path}".replace("/", "_").replace("\\", "_")

        # Limpar caracteres inválidos
        filename = re.sub(r"[^\w\-_.]", "_", filename)
        filename = re.sub(r"_{2,}", "_", filename).strip("_")

        # Garantir extensão .md
        if not filename.endswith(".md"):
            filename += ".md"

        return filename

    def _save_file(self, content: str, filepath: str):
        """Salva conteúdo em arquivo."""
        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            self.logger.info(f"Arquivo salvo: {filepath}")

        except Exception as e:
            raise WebScrapingError(f"Erro ao salvar arquivo {filepath}: {e}") from e

    def clear_cache(self):
        """Limpa o cache."""
        if self.cache_manager:
            self.cache_manager.clear()
            self.logger.info("Cache limpo")

    def get_stats(self) -> dict[str, Any]:
        """Retorna estatísticas do scraper."""
        return {
            "docling_available": DOCLING_AVAILABLE,
            "cache_enabled": self.config.enable_cache,
            "version": __version__,
            "config": asdict(self.config),
        }
