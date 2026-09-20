import urllib.request
import urllib.error
import ssl
import re

TRACKING_LINK = (
    'https://track.atlassian.com/tracking/8006360e-91e4-42a0-ab46-638d2a5b4b61'
    '?m=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0cmlnZ2VySWQiOiJhcmk6Y2xvdWQ6cG9zdC1vZmZpY2'
    'U6OnRyaWdnZXIvaW52aXRhdGlvbnMtYmV0dGVyLW5vdGlmaWNhdGlvbi1pbnZpdGUtdXNlci8zODAwM2QxMDYxMWIxYmE1'
    'NWFjMjg0NzVhYmUyZDlkZiIsIm1lc3NhZ2VUZW1wbGF0ZUlkIjoiaW52aXRhdGlvbnMtYmV0dGVyLW5vdGlmaWNhdGlv'
    'bi1pbnZpdGUtdXNlciIsInJlY2lwaWVudCI6eyJ1c2VyQXJpIjoiYXJpOmNsb3VkOmlkZW50aXR5Ojp1c2VyLzcxMjAy'
    'MDpkY2I0ZWY2MS0xZDY1LTRmYTctOTVmMi0wYWZiNDcxZjA0ODEiLCJ0eXBlIjoiQWNjb3VudElkIn0sImVudGl0eSI6'
    'eyJjb250YWluZXJJZCI6ImFyaTpjbG91ZDpwbGF0Zm9ybTo6b3JnLzA3MTZmNGY0LTc3NzctNDdlNi04MTczLTk3Nzk0'
    'MjM0ZThkZCIsIndvcmtzcGFjZUlkIjoiYXJpOmNsb3VkOnBsYXRmb3JtOjpvcmcvMDcxNmY0ZjQtNzc3Ny00N2U2LTgx'
    'NzMtOTc3OTQyMzRlOGRkIn0sImlhdCI6MTc4OTkyOTE5MX0.J-TX6iOqhY_kFUVgsm4r0dR7qV0alDdafRNzwjmhGfE&j=1'
)

def follow():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    redirects = []
    
    class RedirectCapture(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, hdrs, newurl):
            redirects.append((code, newurl))
            return super().redirect_request(req, fp, code, msg, hdrs, newurl)
    
    opener = urllib.request.build_opener(
        RedirectCapture(),
        urllib.request.HTTPSHandler(context=ctx)
    )
    
    req = urllib.request.Request(TRACKING_LINK, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
    })
    
    try:
        resp = opener.open(req, timeout=15)
        print('Final URL:', resp.geturl())
        print('Redirects:', redirects)
        body = resp.read().decode('utf-8', errors='replace')
        print('Body:', body[:2000])
    except urllib.error.HTTPError as e:
        print('HTTP Error:', e.code)
        loc = e.headers.get('Location', '')
        print('Location:', loc)
        body = e.read().decode('utf-8', errors='replace')
        print('Body:', body[:1000])
        print('Redirects so far:', redirects)
    except Exception as ex:
        print('Error:', type(ex).__name__, str(ex))
        print('Redirects so far:', redirects)

if __name__ == '__main__':
    follow()
