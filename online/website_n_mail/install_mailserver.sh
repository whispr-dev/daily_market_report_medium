
#!/bin/bash
set -e

echo "[✓] Installing Postfix + Dovecot..."

# Update system
apt update && apt upgrade -y

# Install mail stack
apt install -y postfix dovecot-core dovecot-imapd dovecot-pop3d dovecot-lmtpd dovecot-sieve dovecot-managesieved mailutils certbot

echo "[✓] Configuring Postfix..."
# Set domain and hostname
MAILDOMAIN="yourdomain.com"
MAILUSER="mailuser"

# Postfix main.cf (basic setup)
postconf -e "myhostname = mail.$MAILDOMAIN"
postconf -e "myorigin = /etc/mailname"
postconf -e "mydestination = $MAILDOMAIN, localhost"
postconf -e "relayhost ="
postconf -e "mynetworks = 127.0.0.0/8"
postconf -e "mailbox_size_limit = 0"
postconf -e "recipient_delimiter = +"
postconf -e "inet_interfaces = all"
postconf -e "inet_protocols = all"
postconf -e "home_mailbox = Maildir/"

echo "$MAILDOMAIN" > /etc/mailname

# Dovecot config
echo "[✓] Configuring Dovecot..."

# Enable maildir
sed -i "s|^#mail_location =.*|mail_location = maildir:~/Maildir|" /etc/dovecot/conf.d/10-mail.conf

# Authentication settings
sed -i "s|^#disable_plaintext_auth = yes|disable_plaintext_auth = yes|" /etc/dovecot/conf.d/10-auth.conf
sed -i "s|^auth_mechanisms =.*|auth_mechanisms = plain login|" /etc/dovecot/conf.d/10-auth.conf

# Enable PAM auth
sed -i "s|^!include auth-system.conf.ext|#!include auth-system.conf.ext|" /etc/dovecot/conf.d/10-auth.conf
echo "!include auth-passwdfile.conf.ext" >> /etc/dovecot/conf.d/10-auth.conf

# Create virtual user
echo "[✓] Adding mail user..."
useradd $MAILUSER -m -s /sbin/nologin
echo "$MAILUSER:changeme" | chpasswd

mkdir -p /home/$MAILUSER/Maildir
chown -R $MAILUSER: /home/$MAILUSER/Maildir

# Create password file for dovecot
echo "$MAILUSER:{PLAIN}changeme" > /etc/dovecot/users
chmod 640 /etc/dovecot/users
chown root:dovecot /etc/dovecot/users

# Dovecot password file config
cat <<EOF > /etc/dovecot/conf.d/auth-passwdfile.conf.ext
passdb {
  driver = passwd-file
  args = scheme=PLAIN /etc/dovecot/users
}
userdb {
  driver = passwd
}
EOF

# Enable services
systemctl restart postfix dovecot
systemctl enable postfix dovecot

echo "[✓] Obtaining SSL cert via Let's Encrypt (manually run if needed)..."
echo "Run: certbot certonly --standalone -d mail.$MAILDOMAIN"

echo "[✓] Mail server setup complete. IMAP ready at mail.$MAILDOMAIN for user $MAILUSER"
