from curses import wrapper
from curses import initscr
from cursesmenu import Menu

def doExit():
  exit(0)

def constructMenu(stdscreen, items):
  menu = Menu(items, stdscreen)
  # print("Menu is: " + str(menu))
  result = menu.display()
  # print("Result is: " + result)
  return result

def showMenu(items):
  return wrapper(constructMenu, items)
