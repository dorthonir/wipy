import hardware
import serwer
import app

server = serwer.Server()
module = hardware.ADS1115()
main = app.App(server,module)

main.init()
main.loop()