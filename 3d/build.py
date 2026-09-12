"""Inline house.glb into index.html so the viewer is a single file (works from file:// and GitHub Pages)."""
import base64, os
d = os.path.dirname(os.path.abspath(__file__))
glb = base64.b64encode(open(os.path.join(d, 'house.glb'), 'rb').read()).decode()
html = open(os.path.join(d, 'viewer.template.html')).read().replace('__GLB_BASE64__', glb)
open(os.path.join(d, 'index.html'), 'w').write(html)
print('wrote index.html', len(html) // 1024, 'KB')
