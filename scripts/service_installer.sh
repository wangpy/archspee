SERVICE_NAME=archspee
sudo rm /opt/$SERVICE_NAME
sudo ln -s $PWD /opt/$SERVICE_NAME
sudo rm /etc/systemd/system/multi-user.target.wants/$SERVICE_NAME.service
sudo rm /etc/systemd/system/$SERVICE_NAME.service
sudo ln -s $PWD/samples/$SERVICE_NAME.service /etc/systemd/system/
sudo ln -s /etc/systemd/system/$SERVICE_NAME.service /etc/systemd/system/multi-user.target.wants/
sudo systemctl daemon-reload
sudo systemctl start $SERVICE_NAME.service

