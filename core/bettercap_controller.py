import subprocess
import os
import signal
import time
import json
import tempfile

class BettercapController:
    def __init__(self):
        self.process = None
        self.temp_script = None
        
    def create_proxy_script(self, blocked_domains):
        script_content = f"""
function onRequest(req, res) {{
    var host = req.Host;
    if (host === undefined) {{
        host = req.GetHeader("Host");
    }}
    if (host) {{
        var blocked = {json.dumps(blocked_domains)};
        for (var i = 0; i < blocked.length; i++) {{
            if (host.indexOf(blocked[i]) !== -1) {{
                log_info("Blocking: " + host);
                res.Status = 403;
                res.Body = "<html><body><h1>403 Forbidden</h1><p>This domain is blocked.</p></body></html>";
                return;
            }}
        }}
    }}
}}
"""
        fd, path = tempfile.mkstemp(suffix='.js', prefix='bettercap_')
        with os.fdopen(fd, 'w') as f:
            f.write(script_content)
        return path
        
    def start(self, interface, gateway, blocked_domains, log_callback=None):
        try:
            self.temp_script = self.create_proxy_script(blocked_domains)
            commands = f"""
net.probe on
set arp.spoof.targets {gateway}
arp.spoof on
set http.proxy.script {self.temp_script}
http.proxy on
set https.proxy.script {self.temp_script}
https.proxy on
"""
            cmd = ['sudo', 'bettercap', '-eval', commands, '-iface', interface]
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, preexec_fn=os.setsid)
            time.sleep(3)
            if self.process.poll() is not None:
                stderr = self.process.stderr.read()
                return False, f"Bettercap exited: {stderr}"
            if log_callback:
                log_callback("Bettercap started successfully")
            return True, "Bettercap started successfully"
        except Exception as e:
            return False, f"Failed to start Bettercap: {str(e)}"
            
    def stop(self):
        try:
            if self.process:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=5)
            if self.temp_script and os.path.exists(self.temp_script):
                os.unlink(self.temp_script)
            return True, "Bettercap stopped"
        except Exception as e:
            return False, f"Error stopping Bettercap: {str(e)}"
            
    def update_blocklist(self, blocked_domains):
        if self.process and self.temp_script:
            new_script = self.create_proxy_script(blocked_domains)
            os.replace(new_script, self.temp_script)