import os
files = os.listdir("C:\\Users\\Igor\\Desktop\\Job-Seeker")
print(files)

stack = {
   'language': None,
}

if "requirements.txt" in files:
    print("There is a requirements.txt file!")

if any(f.endswith('.py') for f in files):
    print('Python is here!')
    stack['language'] = 'Python'
    

try:
    with open("C:\\Users\\Igor\\Desktop\\Job-Seeker\\requirements.txt", "r") as f:
        content = f.read()
        print(content)
except FileNotFoundError as e:
    print(f'Error occurred: {e}')