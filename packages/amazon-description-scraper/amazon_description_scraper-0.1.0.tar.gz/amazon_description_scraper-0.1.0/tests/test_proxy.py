from amzsc.modules.proxy import get_proxy, ProxyRequest


def test_get_proxy():
    """Test the get_proxy function."""
    # Assuming you have a valid API key for testing
    proxy_key = "demo_proxy_key"
    proxy = get_proxy(proxy_key)
    assert proxy is None, "Proxy should be None for invalid API key"


def test_get_proxy_live():
    """Test the ProxyRequest.is_proxy_live method."""
    proxy_key = "demo_proxy_key"
    proxy_cli = ProxyRequest(api_key=proxy_key)
    proxy = proxy_cli.get_new_proxy()
    assert proxy is None, "Proxy should be None for invalid API key"
    is_proxy_live = ProxyRequest.is_proxy_live(proxy=proxy)
    assert is_proxy_live is False, "Proxy should not be live for invalid API key"
