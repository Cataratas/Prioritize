import tkinter
from tkinter import ttk
import sv_ttk
import psutil


def sort_treeview(tv, col_id, reverse):
    data = [(tv.set(child, col_id), child) for child in tv.get_children("")]
    data.sort(reverse=reverse)

    for index, (val, child) in enumerate(data):
        tv.move(child, "", index)

    tv.heading(col_id, command=lambda: sort_treeview(tv, col_id, not reverse))


def addProcess(priority):
    if selection := tree.selection():
        pid = int(tree.item(selection[0])["values"][1])
        for i, process in enumerate(processes):
            if process[0] == pid:
                processes[i] = (pid, priority)
        psutil.Process(pid).nice(priority)
        refresh()


def getProcessPriority(nice):
    if psutil.ABOVE_NORMAL_PRIORITY_CLASS == nice:
        return "Above Normal"
    elif psutil.NORMAL_PRIORITY_CLASS == nice:
        return "Normal"
    elif psutil.BELOW_NORMAL_PRIORITY_CLASS == nice:
        return "Below Normal"
    elif psutil.HIGH_PRIORITY_CLASS == nice:
        return "High"
    elif psutil.REALTIME_PRIORITY_CLASS == nice:
        return "Real Time"
    elif psutil.IDLE_PRIORITY_CLASS == nice:
        return "Low"


def getProcesses():
    for process in psutil.process_iter():
        try:
            yield f" {process.name()}", process.pid, getProcessPriority(process.nice())
        except psutil.AccessDenied:
            continue


def handle_right_click(event):
    if item := tree.identify_row(event.y):
        tree.selection_set(item)
        menu.post(event.x_root, event.y_root)


def setProcessesPriority():
    [psutil.Process(process[0]).nice(process[1]) for process in processes]
    root.after(20000, setProcessesPriority)


def refresh():
    [tree.delete(child) for child in tree.get_children()]
    [tree.insert("", "end", values=process, tags=("row", )) for process in getProcesses()]

    if sort == 0:
        sort_treeview(tree, "Name", False)


def setSort(id):
    global sort
    sort = id
    if sort == 0:
        sort_treeview(tree, "Name", False)


root = tkinter.Tk()
root.geometry("450x800")
root.title("Prioritize")

menu = tkinter.Menu(root, tearoff=0)
submenu = tkinter.Menu(menu, tearoff=0)
submenu.add_command(label="Real Time", command=lambda: addProcess(psutil.REALTIME_PRIORITY_CLASS))
submenu.add_command(label="High", command=lambda: addProcess(psutil.HIGH_PRIORITY_CLASS))
submenu.add_command(label="Above Normal", command=lambda: addProcess(psutil.ABOVE_NORMAL_PRIORITY_CLASS))
submenu.add_command(label="Normal", command=lambda: addProcess(psutil.NORMAL_PRIORITY_CLASS))
submenu.add_command(label="Below Normal", command=lambda: addProcess(psutil.BELOW_NORMAL_PRIORITY_CLASS))
submenu.add_command(label="Low", command=lambda: addProcess(psutil.IDLE_PRIORITY_CLASS))
menu.add_cascade(label="Set Priority", menu=submenu)
menu.add_cascade(label="Refresh", command=refresh)

tree = ttk.Treeview(root, columns=("Name", "PID", "Priority"), show='headings', height=800, selectmode='browse')
tree["selectmode"] = "extended"

tree.column("# 1", width=250)
tree.heading("# 1", text="  Name", anchor=tkinter.W, command=lambda: setSort(0))
tree.column("# 2", width=75, anchor=tkinter.CENTER)
tree.heading("# 2", text="PID", command=lambda: setSort(1))
tree.column("# 3", width=115, anchor=tkinter.CENTER)
tree.heading("# 3", text="Priority")
tree.bind("<Button-3>", handle_right_click)

processes, sort = [], -1
refresh()
setProcessesPriority()

tree.pack()
sv_ttk.set_theme("light")
root.mainloop()
