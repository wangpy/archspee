SERVICE_NAME=archspee
sudo systemctl stop $SERVICE_NAME.service
sudo rm /etc/systemd/system/multi-user.target.wants/$SERVICE_NAME.service
sudo rm /etc/systemd/system/$SERVICE_NAME.service
sudo rm /opt/$SERVICE_NAME
sudo systemctl daemon-reload
