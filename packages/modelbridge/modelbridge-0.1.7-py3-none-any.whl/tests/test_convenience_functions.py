"""
Test convenience functions and exports
"""
import pytest
from unittest.mock import patch, AsyncMock
import asyncio


class TestConvenienceFunctions:
    """Test convenience functions in __init__.py"""

    @pytest.mark.asyncio
    async def test_create_bridge_default(self):
        """Test create_bridge function with default parameters"""
        from modelbridge import create_bridge
        
        # Mock initialize to avoid needing real API keys
        with patch('modelbridge.ModelBridge.initialize', new_callable=AsyncMock) as mock_init:
            mock_init.return_value = True
            
            bridge = await create_bridge()
            
            assert bridge is not None
            assert hasattr(bridge, 'generate_text')
            assert hasattr(bridge, 'generate_structured_output')
            mock_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_bridge_with_config(self):
        """Test create_bridge function with config path"""
        from modelbridge import create_bridge
        
        with patch('modelbridge.ModelBridge') as MockBridge:
            mock_instance = AsyncMock()
            mock_instance.initialize.return_value = True
            MockBridge.return_value = mock_instance
            
            bridge = await create_bridge(config_path="test_config.yaml")
            
            MockBridge.assert_called_once_with("test_config.yaml")
            mock_instance.initialize.assert_called_once()

    def test_all_exports_available(self):
        """Test that all expected exports are available"""
        import modelbridge
        
        # Check main classes
        assert hasattr(modelbridge, 'ModelBridge')
        assert hasattr(modelbridge, 'IntelligentRouter')
        
        # Check base classes
        assert hasattr(modelbridge, 'BaseModelProvider')
        assert hasattr(modelbridge, 'GenerationRequest')
        assert hasattr(modelbridge, 'GenerationResponse')
        assert hasattr(modelbridge, 'ModelMetadata')
        assert hasattr(modelbridge, 'ModelCapability')
        
        # Check convenience function
        assert hasattr(modelbridge, 'create_bridge')
        assert callable(modelbridge.create_bridge)

    def test_version_info(self):
        """Test version information"""
        import modelbridge
        
        assert hasattr(modelbridge, '__version__')
        assert isinstance(modelbridge.__version__, str)
        assert modelbridge.__version__ == "0.1.0"
        
        assert hasattr(modelbridge, '__author__')
        assert hasattr(modelbridge, '__email__')

    def test_module_docstring(self):
        """Test module has docstring"""
        import modelbridge
        
        assert modelbridge.__doc__ is not None
        assert "ModelBridge" in modelbridge.__doc__