from lib.input import Input

a = Input("fluka/run.inp")
a.transRandom()
a.defectRandom()

a.write("test.inp")
