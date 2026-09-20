import subprocess
import re
import urllib.request
import urllib.error
import ssl

def main():
    p = subprocess.Popen(
        ['ssh', 'root@195.90.215.204', 'docker exec mailcowdockerized-dovecot-mailcow-1 doveadm fetch -u ai@coneza.de text.utf8 mailbox INBOX uid 5'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = p.communicate()
    text = out.decode('utf-8', errors='replace')

    # Get the CI0 tracking link (primary CTA)
    ci0_links = re.findall(r'https://use1-track\.atlassian\.com/CI0/[^\s\r\n\x0c"\']+', text)
    
    if not ci0_links:
        print("No CI0 links found. Looking for other invitation URLs...")
        print(text[-3000:])
        return

    # Clean the link
    link = ci0_links[0].rstrip('"\'\\').rstrip('=452').rstrip()
    # The =452 at the end is quoted-printable line length marker, not part of URL
    # Properly clean: strip trailing =NNN or similar artifacts
    link = re.sub(r'=\d+["\']?$', '', link)
    print(f"Invitation CTA link:\n{link}\n")
    
    # Follow with redirects to find final URL
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    print("Following redirects...")
    try:
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
        req = urllib.request.Request(link, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        resp = opener.open(req, timeout=15)
        final_url = resp.geturl()
        print(f"Final URL: {final_url}")
        body = resp.read(5000).decode('utf-8', errors='replace')
        # Find any invite/token links in the response
        invite_links = re.findall(r'https?://[^\s"\'<>]+(?:invite|accept|join|token|signup)[^\s"\'<>]+', body)
        if invite_links:
            print("\nInvite-related links in response:")
            for il in invite_links:
                print(il)
        print("\nBody preview (first 1000 chars):")
        print(body[:1000])
    except Exception as ex:
        print(f"Error following link: {ex}")

if __name__ == '__main__':
    main()
