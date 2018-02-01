import os
import subprocess


directory_in_str = '/home/marin/ppj/lab1_python/tests/1labos-2011-2012'
directory = os.fsencode(directory_in_str)

for file in os.listdir(directory):
    filename = os.fsdecode(file)
    folder = os.path.join(directory_in_str, filename)
    pom1 = os.path.join(folder, 'test.lan')
    pom2 = os.path.join(folder, 'moj.out')

    process = subprocess.Popen("python3.6 /home/marin/ppj/lab1_python/source/GLA.py {pom1} {pom2}".format(**locals()),
                     shell=True)
    process.wait()
    pom1 = os.path.join(folder, 'test.in')
    process2 = subprocess.Popen(
        "python3.6 /home/marin/ppj/lab1_python/source/analizator/LA.py {pom1}".format(**locals()),
        shell=True
    )
    process2.wait()
    with open(os.path.join(folder, 'test.out'), 'r') as content_file:
        contentfirst = content_file.read()
    with open(os.path.join(folder, 'moj.out'), 'r') as content_file:
        contentsecond = content_file.read()
    if contentfirst == contentsecond:
        print(True, folder)
    else:
        print(False, folder)
