from aclib.cv import DotsetLib, Image

dl = DotsetLib.fromfile(r"E:\#project\python\PersonalLib\.test\ddd")

for d in dl:
    d.print()
r = Image.fromfile('ym.png').finddotset(dl, 'ICON_频道筛选', similarity=0.65)
print(r.offset(0, -30))
