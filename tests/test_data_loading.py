import sys
import tempfile
import types
from pathlib import Path
import unittest


streamlit_stub = types.ModuleType("streamlit")
streamlit_stub.cache_data = lambda func=None, **kwargs: (lambda f: f) if func is None else func
streamlit_stub.set_page_config = lambda *args, **kwargs: None
streamlit_stub.markdown = lambda *args, **kwargs: None
streamlit_stub.sidebar = None
streamlit_stub.radio = lambda *args, **kwargs: None
streamlit_stub.multiselect = lambda *args, **kwargs: None
streamlit_stub.selectbox = lambda *args, **kwargs: None
streamlit_stub.slider = lambda *args, **kwargs: None
streamlit_stub.checkbox = lambda *args, **kwargs: None
streamlit_stub.columns = lambda *args, **kwargs: []
streamlit_stub.expander = lambda *args, **kwargs: None
streamlit_stub.pydeck_chart = lambda *args, **kwargs: None
streamlit_stub.dataframe = lambda *args, **kwargs: None
streamlit_stub.info = lambda *args, **kwargs: None
streamlit_stub.bar_chart = lambda *args, **kwargs: None
streamlit_stub.markdown = lambda *args, **kwargs: None
streamlit_stub.columns = lambda *args, **kwargs: []
sys.modules.setdefault("streamlit", streamlit_stub)

pydeck_stub = types.ModuleType("pydeck")
pydeck_stub.ViewState = lambda *args, **kwargs: None
pydeck_stub.Layer = lambda *args, **kwargs: None
pydeck_stub.Deck = lambda *args, **kwargs: None
sys.modules.setdefault("pydeck", pydeck_stub)

from evox_app import resolve_data_file


class ResolveDataFileTests(unittest.TestCase):
    def test_resolve_data_file_returns_existing_absolute_path(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as handle:
            path = Path(handle.name)

        try:
            resolved = resolve_data_file(str(path))
            self.assertEqual(resolved, path)
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
