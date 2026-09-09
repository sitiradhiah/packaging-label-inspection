"""Verify all buttons remain reachable on small and scaled displays."""
import tkinter as tk
from dashboard import Dashboard
for scaling in [1.33,2.0]:
 root=tk.Tk();root.tk.call('tk','scaling',scaling);app=Dashboard(root,rb3=False)
 for size in ['640x480','800x600','1180x820']:
  root.geometry(size);root.update()
  region=list(map(float,app.page.cget('scrollregion').split()))
  for button in [app.start_button,app.stop_button,app.load_button,app.check_button,app.excel_button,app.folder_button]:
   x=button.winfo_rootx()-app.shell.winfo_rootx();y=button.winfo_rooty()-app.shell.winfo_rooty()
   assert x>=0 and y>=0 and x+button.winfo_width()<=region[2] and y+button.winfo_height()<=region[3],(size,button.cget('text'))
   parent=button.master
   assert button.winfo_x()+button.winfo_width()<=parent.winfo_width(),button.cget('text')
  app.page.yview_moveto(1);root.update()
  assert app.folder_button.winfo_rooty()+app.folder_button.winfo_height()<=app.page.winfo_rooty()+app.page.winfo_height()
  app.page.yview_moveto(0)
  print('PASS',size,'scale',scaling)
 for pending in root.tk.call("after","info"):root.after_cancel(pending)
 app.close()
