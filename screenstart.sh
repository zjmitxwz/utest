screen_name="main"
screen -dmS $screen_name
cmd="/root/code/mainstart.sh"
screen -x -S $screen_name -p 0 -X stuff "$cmd"
screen -x -S $screen_name -p 0 -X stuff $'\n'
