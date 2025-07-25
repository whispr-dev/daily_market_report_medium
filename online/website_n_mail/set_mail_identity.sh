
#!/bin/bash
set -e

# Define target From address
FROM_ADDR="noreply@whispr.dev"
MAILDOMAIN="whispr.dev"
MAILUSER="wofl"

echo "[✓] Setting system mailname..."
echo "$MAILDOMAIN" | sudo tee /etc/mailname > /dev/null

echo "[✓] Configuring Postfix main.cf..."
sudo postconf -e "myorigin = /etc/mailname"
sudo postconf -e "myhostname = mail.$MAILDOMAIN"

echo "[✓] Creating canonical map..."
cat <<EOF | sudo tee /etc/postfix/canonical
$MAILUSER    $FROM_ADDR
root         $FROM_ADDR
EOF

sudo postmap /etc/postfix/canonical
sudo postconf -e "canonical_maps = hash:/etc/postfix/canonical"

echo "[✓] Reloading Postfix..."
sudo systemctl reload postfix

echo "[✔] All mail will now appear from: $FROM_ADDR"
