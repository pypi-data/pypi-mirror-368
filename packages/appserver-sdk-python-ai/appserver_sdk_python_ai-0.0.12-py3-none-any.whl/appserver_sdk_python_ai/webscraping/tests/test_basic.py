# appserver_sdk_python_ai/webscraping/tests/test_basic.py
"""
Testes básicos para o módulo de webscraping.
"""

import tempfile
from unittest.mock import Mock, patch

import pytest

from .. import health_check, quick_scrape
from ..core.config import ScrapingConfig
from ..core.exceptions import ValidationError
from ..core.models import ScrapingResult, ScrapingStatus
from ..utils.cache import CacheManager, MemoryCache
from ..utils.cleaner import ContentCleaner
from ..utils.validators import ContentValidator, URLValidator

# Configuração para testes
# Removido sys._called_from_test = True pois não é necessário


class TestScrapingConfig:
    """Testes para configuração de scraping."""

    def test_default_config(self):
        """Testa configuração padrão."""
        config = ScrapingConfig()

        assert config.timeout == 30
        assert config.clean_html
        assert config.include_images
        assert not config.enable_cache
        assert config.retry_attempts == 3

    def test_custom_config(self):
        """Testa configuração customizada."""
        config = ScrapingConfig(
            timeout=60, clean_html=False, enable_cache=True, retry_attempts=5
        )

        assert config.timeout == 60
        assert not config.clean_html
        assert config.enable_cache
        assert config.retry_attempts == 5

    def test_get_headers(self):
        """Testa obtenção de headers."""
        config = ScrapingConfig(
            user_agent="Test Agent", headers={"Accept": "text/html"}
        )

        headers = config.get_headers()

        assert headers["User-Agent"] == "Test Agent"
        assert headers["Accept"] == "text/html"
        assert "Accept-Language" in headers


class TestScrapingResult:
    """Testes para resultado de scraping."""

    def test_successful_result(self):
        """Testa resultado de sucesso."""
        result = ScrapingResult(
            url="https://example.com",
            title="Test Page",
            content="# Test\n\nContent here",
            metadata={"author": "Test"},
            success=True,
            processing_time=1.5,
        )

        assert result.success
        assert result.status == ScrapingStatus.SUCCESS
        assert result.url == "https://example.com"
        assert result.content_length > 0
        assert result.timestamp is not None

    def test_failed_result(self):
        """Testa resultado de falha."""
        result = ScrapingResult(
            url="https://example.com",
            title="",
            content="",
            metadata={},
            success=False,
            error="Network error",
        )

        assert not result.success
        assert result.status == ScrapingStatus.FAILED
        assert result.error == "Network error"
        assert result.content_length == 0

    def test_to_dict(self):
        """Testa conversão para dicionário."""
        result = ScrapingResult(
            url="https://example.com",
            title="Test",
            content="Content",
            metadata={"key": "value"},
            success=True,
        )

        result_dict = result.to_dict()

        assert result_dict["url"] == "https://example.com"
        assert result_dict["success"]
        assert result_dict["status"] == "success"
        assert "timestamp" in result_dict


class TestURLValidator:
    """Testes para validador de URLs."""

    def test_valid_urls(self):
        """Testa URLs válidas."""
        valid_urls = [
            "https://example.com",
            "http://test.org/path",
            "https://subdomain.example.com/page.html",
        ]

        for url in valid_urls:
            assert URLValidator.validate_url(url)

    def test_invalid_schemes(self):
        """Testa esquemas inválidos."""
        invalid_urls = [
            "ftp://example.com",
            "file:///path/to/file",
            "javascript:alert('test')",
        ]

        for url in invalid_urls:
            with pytest.raises(ValidationError):
                URLValidator.validate_url(url)

    def test_blocked_domains(self):
        """Testa domínios bloqueados."""
        blocked_urls = [
            "https://facebook.com",
            "https://localhost:8080",
            "http://127.0.0.1",
        ]

        for url in blocked_urls:
            with pytest.raises(ValidationError):
                URLValidator.validate_url(url)

    def test_blocked_extensions(self):
        """Testa extensões bloqueadas."""
        blocked_urls = [
            "https://example.com/file.pdf",
            "https://example.com/image.jpg",
            "https://example.com/archive.zip",
        ]

        for url in blocked_urls:
            with pytest.raises(ValidationError):
                URLValidator.validate_url(url)

    def test_normalize_url(self):
        """Testa normalização de URLs."""
        test_cases = [
            (
                "https://example.com/page?utm_source=google&id=123",
                "https://example.com/page?id=123",
            ),
            ("https://example.com/page#section", "https://example.com/page"),
        ]

        for original, expected in test_cases:
            normalized = URLValidator.normalize_url(original)
            assert normalized == expected

    def test_same_domain(self):
        """Testa verificação de mesmo domínio."""
        assert URLValidator.is_same_domain(
            "https://example.com/page1", "https://example.com/page2"
        )

        assert not URLValidator.is_same_domain(
            "https://example.com", "https://other.com"
        )

    def test_absolute_url(self):
        """Testa verificação de URL absoluta."""
        assert URLValidator.is_absolute_url("https://example.com")
        assert not URLValidator.is_absolute_url("/relative/path")
        assert not URLValidator.is_absolute_url("relative.html")


class TestContentValidator:
    """Testes para validador de conteúdo."""

    def test_valid_content(self):
        """Testa conteúdo válido."""
        content = "Este é um conteúdo de teste com pelo menos vinte palavras para passar na validação mínima de conteúdo do sistema."

        assert ContentValidator.is_valid_content(content)

    def test_short_content(self):
        """Testa conteúdo muito curto."""
        short_content = "Muito curto"

        assert not ContentValidator.is_valid_content(short_content)

    def test_empty_content(self):
        """Testa conteúdo vazio."""
        assert not ContentValidator.is_valid_content("")
        assert not ContentValidator.is_valid_content(None)

    def test_detect_language(self):
        """Testa detecção de idioma."""
        portuguese_text = "Este é um texto em português com várias palavras comuns da língua portuguesa."
        english_text = "This is a text in English with several common words from the English language."

        assert ContentValidator.detect_content_language(portuguese_text) == "pt"
        assert ContentValidator.detect_content_language(english_text) == "en"

    def test_readability_score(self):
        """Testa pontuação de legibilidade."""
        readable_text = (
            "Este é um texto simples. As frases são curtas. As palavras são comuns."
        )
        score = ContentValidator.calculate_readability_score(readable_text)

        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Deve ter boa legibilidade


class TestContentCleaner:
    """Testes para limpeza de conteúdo."""

    def test_remove_scripts(self):
        """Testa remoção de scripts."""
        html = '<html><body><script>alert("test")</script><p>Content</p></body></html>'
        config = ScrapingConfig()

        cleaned = ContentCleaner.clean_html(html, "https://example.com", config)

        assert "<script>" not in cleaned
        assert "alert(" not in cleaned
        assert "<p>Content</p>" in cleaned

    def test_remove_styles(self):
        """Testa remoção de estilos."""
        html = "<html><head><style>body { color: red; }</style></head><body><p>Content</p></body></html>"
        config = ScrapingConfig()

        cleaned = ContentCleaner.clean_html(html, "https://example.com", config)

        assert "<style>" not in cleaned
        assert "color: red" not in cleaned

    def test_remove_ads(self):
        """Testa remoção de elementos de propaganda."""
        html = """
        <html><body>
            <div class="advertisement">Ad content</div>
            <div id="banner">Banner</div>
            <p>Real content</p>
        </body></html>
        """
        config = ScrapingConfig()

        cleaned = ContentCleaner.clean_html(html, "https://example.com", config)

        assert "Ad content" not in cleaned
        assert "Banner" not in cleaned
        assert "Real content" in cleaned

    def test_resolve_relative_urls(self):
        """Testa resolução de URLs relativas."""
        html = '<html><body><a href="/page">Link</a><img src="image.jpg"></body></html>'
        config = ScrapingConfig(include_links=True, include_images=True)

        cleaned = ContentCleaner.clean_html(html, "https://example.com", config)

        assert "https://example.com/page" in cleaned
        assert "https://example.com/image.jpg" in cleaned

    def test_remove_images_config(self):
        """Testa remoção de imagens por configuração."""
        html = '<html><body><p>Text</p><img src="image.jpg" alt="Image"></body></html>'
        config = ScrapingConfig(include_images=False)

        cleaned = ContentCleaner.clean_html(html, "https://example.com", config)

        assert "<img" not in cleaned
        assert "<p>Text</p>" in cleaned


class TestCacheManager:
    """Testes para gerenciador de cache."""

    def setup_method(self):
        """Setup para cada teste."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_manager = CacheManager(self.temp_dir)

    def test_cache_miss(self):
        """Testa cache miss."""
        content = self.cache_manager.get("https://example.com", {}, 3600)
        assert content is None

    def test_cache_set_and_get(self):
        """Testa armazenamento e recuperação do cache."""
        url = "https://example.com"
        headers = {"User-Agent": "Test"}
        content = "<html><body>Test content</body></html>"

        # Armazenar
        self.cache_manager.set(url, headers, content)

        # Recuperar
        cached_content = self.cache_manager.get(url, headers, 3600)

        assert cached_content == content

    def test_cache_stats(self):
        """Testa estatísticas do cache."""
        # Adicionar algumas entradas
        for i in range(3):
            self.cache_manager.set(
                f"https://example{i}.com", {"User-Agent": "Test"}, f"Content {i}"
            )

        stats = self.cache_manager.get_cache_stats()

        assert stats["total_entries"] == 3
        assert stats["total_size_mb"] > 0

    def test_cache_clear(self):
        """Testa limpeza do cache."""
        # Adicionar entrada
        self.cache_manager.set("https://example.com", {}, "content")

        # Verificar que existe
        assert self.cache_manager.get("https://example.com", {}, 3600) is not None

        # Limpar
        self.cache_manager.clear()

        # Verificar que foi limpo
        assert self.cache_manager.get("https://example.com", {}, 3600) is None
        stats = self.cache_manager.get_cache_stats()
        assert stats["total_entries"] == 0


class TestMemoryCache:
    """Testes para cache em memória."""

    def test_memory_cache_basic(self):
        """Testa funcionalidade básica."""
        cache = MemoryCache(max_entries=2)

        # Teste miss
        assert cache.get("key1") is None

        # Teste set/get
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Teste limite de entradas
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Deve remover key1

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_memory_cache_clear(self):
        """Testa limpeza do cache em memória."""
        cache = MemoryCache()

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        assert cache.size() == 2

        cache.clear()

        assert cache.size() == 0
        assert cache.get("key1") is None


class TestHealthCheck:
    """Testes para verificação de saúde."""

    def test_health_check(self):
        """Testa verificação de saúde básica."""
        health = health_check()

        assert "status" in health
        assert "version" in health
        assert "dependencies" in health
        assert "features" in health

        # Status deve ser OK, WARNING ou ERROR
        assert health["status"] in ["OK", "WARNING", "ERROR"]

    def test_dependency_check(self):
        """Testa verificação de dependências."""
        from .. import check_dependencies

        deps = check_dependencies()

        # Dependências básicas devem estar presentes
        assert "requests" in deps
        assert "beautifulsoup4" in deps

        # requests deve estar instalado (necessário para os testes)
        assert deps["requests"] != "NOT_INSTALLED"


@pytest.mark.integration
class TestIntegration:
    """Testes de integração."""

    @patch("requests.get")
    def test_quick_scrape_mock(self, mock_get):
        """Testa scraping rápido com mock."""
        # Mock da resposta HTTP
        mock_response = Mock()
        mock_response.text = (
            "<html><body><h1>Test Page</h1><p>Content</p></body></html>"
        )
        mock_response.headers = {"content-type": "text/html"}
        mock_response.encoding = "utf-8"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Teste
        content = quick_scrape("https://example.com")

        assert isinstance(content, str)
        assert len(content) > 0
        assert "Test Page" in content

    def test_scraping_config_integration(self):
        """Testa integração de configurações."""
        config = ScrapingConfig(timeout=20, clean_html=True, enable_cache=False)

        # Verificar que as configurações são aplicadas corretamente
        headers = config.get_headers()
        assert "User-Agent" in headers

        # Configuração deve ser serializável
        import json
        from dataclasses import asdict

        config_dict = asdict(config)
        json_str = json.dumps(config_dict, default=str)
        assert len(json_str) > 0


# Fixtures para testes
@pytest.fixture
def sample_html():
    """HTML de exemplo para testes."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <meta name="description" content="Test description">
        <script>console.log('test');</script>
        <style>body { margin: 0; }</style>
    </head>
    <body>
        <header>
            <nav>Navigation</nav>
        </header>
        <main>
            <h1>Main Title</h1>
            <article>
                <h2>Article Title</h2>
                <p>This is the main content of the article with <a href="/link">a link</a>.</p>
                <img src="image.jpg" alt="Test image">
                <blockquote>A quote from someone</blockquote>
            </article>
        </main>
        <aside>
            <div class="advertisement">Ad content</div>
            <div class="sidebar">Sidebar content</div>
        </aside>
        <footer>Footer content</footer>
    </body>
    </html>
    """


@pytest.fixture
def mock_scraping_result():
    """Resultado de scraping de exemplo."""
    return ScrapingResult(
        url="https://example.com",
        title="Test Page",
        content="# Test Page\n\nThis is test content.",
        metadata={
            "description": "Test description",
            "author": "Test Author",
            "word_count": 100,
        },
        success=True,
        processing_time=1.5,
    )


# Execução dos testes
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
