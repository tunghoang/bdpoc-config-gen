from app import App
from configs.module_loader import *

def main():
  app = App()
  app.render()
  # st.write(st.session_state["difference_time_range"])

if __name__ == "__main__":
  main()
