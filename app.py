from urllib.parse import parse_qs

def build_text_area(contents):
    return """
<body>
    <form action="/submit" method="post">
        <textarea name="message" rows="8" cols="50">%s</textarea>
        <br>
        <input type="submit" value="Submit">
    </form>
</body>
</html>
""" % contents

class VM:
    def __init__(self, code, step_limit=100000):
        self.code = code
        self.stack = []
        self.registers = {
            "a": 0,
            "b": 0,
            "c": 0,
            "d": 0,
            "insp": 1,
        }
        self.labels = {}
        self.steps = 0
        self.step_limit = step_limit
        self.error = None
        self.complete = False

    def run(self):
        self.resolve_labels()

        while not self.complete and self.error is None:
            self.step()
        #if self.error is not None:
            #print(self.error)
        
    def resolve_labels(self):
        line_no = 0
        for line in self.code:
            line_no += 1
            splt = line.split()
            if len(splt) == 1 and line.split()[0].endswith(":"):
                if self.labels.__contains__(splt[0]):
                    self.error = "Duplicate label `%s`" % splt[0]
                    return
                self.labels[splt[0]] = line_no
    
    def step(self):
        if self.complete or self.error:
            return
        if self.step_limit > 0 and self.steps >= self.step_limit:
            self.error = "Program reached step limit"
            return
        insp = self.registers["insp"]
        if insp > len(self.code):
            self.complete = True
            return
        if insp <= 0:
            self.error = "Invalid instruction pointer value!"
        self.steps += 1
        self.exec_line(self.code[insp - 1])
    
    def exec_line(self, line):
        tokens = line.split()
        if tokens == [] or tokens[0][0] == '#' or (len(tokens) == 1 and tokens[0].endswith(":")):
            self.registers["insp"] += 1
            return
        elif tokens[0] == "lodi":
            self.lodi(tokens)
        elif tokens[0] == "lodr":
            self.lodr(tokens)
        elif tokens[0] == "addi":
            self.addi(tokens)
        elif tokens[0] == "addr":
            self.addr(tokens)
        elif tokens[0] == "muli":
            self.muli(tokens)
        elif tokens[0] == "mulr":
            self.mulr(tokens)
        elif tokens[0] == "push":
            self.push(tokens)
        elif tokens[0] == "pop":
            self.pop(tokens)
        elif tokens[0] == "peek":
            self.peek(tokens)
        elif tokens[0] == "jump":
            self.jump(tokens)
        elif tokens[0] == "jzer":
            self.jzer(tokens)
        elif tokens[0] == "halt":
            self.halt(tokens)
        elif tokens[0] == "call":
            self.call(tokens)
        elif tokens[0] == "retn":
            self.retn(tokens)
        else:
            self.error = "Unrecognized command %s" % tokens[0]
    
    def call(self, tokens):
        if len(tokens) != 2:
            self.error = "Invalid # of arugments, try `call [label]`"
            return
        try:
            old_sp = self.registers["insp"]
            self.registers["insp"] = self.labels[tokens[1]]
            self.stack.append(old_sp)
        except:
            self.error = "Attempted to call to unrecognized label `%s`" % tokens[1]
    
    def retn(self, tokens):
        if len(tokens) != 1:
            self.error = "Invalid # of arguments, try `retn`"
            return
        if len(self.stack) == 0:
            self.error = "Attempted to return with empty stack"
            return
        self.registers["insp"] = self.stack.pop() + 1
        

    def jump(self, tokens):
        if len(tokens) != 2:
            self.error = "Invalid number of arguments, try `jump [label]`"
            return
        try:
            self.registers["insp"] = self.labels[tokens[1]]
        except:
            self.error = "Attempted to jump to unrecognized label `%s`" % tokens[1]
    
    def jzer(self, tokens):
        if len(tokens) != 3:
            self.error = "Invalid number of arguments, try `jzer [register] [line]`"
            return
        try:
            if self.registers[tokens[1]] == 0:
                self.registers["insp"] = self.labels[tokens[2]]
            else:
                self.registers["insp"] += 1
        except:
            self.error = "Could not jump to location %s based off of register %s" % tokens[2], tokens[1]
            
    
    def push(self, tokens):
        if len(tokens) != 2:
            self.error = "Invalid number of arguments, try `push [register]"
            return
        try:
            self.stack.append(self.registers[tokens[1]])
            self.registers["insp"] += 1
        except:
            self.error = "Attempted to push from unrecognized register '%s'" % tokens[1]            

    def pop(self, tokens):
        if len(tokens) != 2:
            self.error = "Invalid number of arguments, try `pop [register]"
        if len(self.stack) == 0:
            self.error = "Attempted to pop off empty stack"
            return
        try:
            self.registers[tokens[1]] = self.stack.pop()
            self.registers["insp"] += 1
        except:
            self.error = "Attempted to pop to register '%s'" % tokens[1]

    def peek(self, tokens):
        if len(tokens) != 3:
            self.error = "Invalid number of arguments, try `peek [register] [number]`"
        if len(self.stack) == 0:
            self.error = "Attempted to peek empty stack"
            return
        try:
            self.registers[tokens[1]] = self.stack[len(self.stack) - int(tokens[2]) - 1]
            self.registers["insp"] += 1
        except:
            self.error = "could not peek stack index `%s` to register `%s`" % (tokens[2], tokens[1])

    def lodi(self, tokens):
        if len(tokens) != 3:
            self.error = "Invalid number of arguments in lodi: try `lodi [register] [value]`"
        else:
            try:
                self.registers[tokens[1]] = int(tokens[2])
                self.registers["insp"] += 1
            except:
                self.error = "Could not load value `%s` into register `%s`" % (tokens[2], tokens[1])
    
    def lodr(self, tokens):
        if len(tokens) != 3:
            self.error = "Invalid number of arguments in lodr: try `lodr [register] [register]`"
        else:
            try:
                self.registers[tokens[1]] = self.registers[tokens[2]]
                self.registers["insp"] += 1
            except:
                self.error = "Could not load value from register" + tokens[2] + " into register " + tokens[1]

    def addi(self, tokens):
        if len(tokens) != 3:
            self.error = "Invalid number of arguments in addi: try `addi [register] [value]`"
        else:
            try:
                self.registers[tokens[1]] += int(tokens[2])
                self.registers["insp"] += 1
            except:
                self.error = "Could not add value " + tokens[2] + " to register " + tokens[1]

    def addr(self, tokens):
        if len(tokens) != 3:
            self.error = "Invalid number of arguments in addr: try `addr [register] [register]`"
        else:
            try:
                self.registers[tokens[1]] += self.registers[tokens[2]]
                self.registers["insp"] += 1
            except:
                self.error = "Could not add register " + tokens[2] + " to register " + tokens[1]

    def muli(self, tokens):
        if len(tokens) != 3:
            self.error = "Invalid number of arguments in muli: try `muli [register] [value]`"
        else:
            try:
                self.registers[tokens[1]] *= int(tokens[2])
                self.registers["insp"] += 1
            except:
                self.error = "Could not multiply value " + tokens[2] + " by register " + tokens[1]

    def mulr(self, tokens):
        if len(tokens) != 3:
            self.error = "Invalid number of arguments in mulr: try `mulr [register] [register]`"
        else:
            try:
                self.registers[tokens[1]] *= self.registers[tokens[2]]
                self.registers["insp"] += 1
            except:
                self.error = "Could not multiply register " + tokens[2] + " by register " + tokens[1]
    
    def halt(self, tokens):
        self.complete = True

    def get_registers(self):
        return (self.registers["a"], self.registers["b"], self.registers["c"], self.registers["d"], self.registers["insp"])
    def get_stack(self):
        return self.stack
    def get_err_string(self):
        if self.error is None:
            return ""
        return self.error

def build_stack(cpu):
    stck = cpu.get_stack()
    stck.reverse()
    print(stck)
    html = '<ol start="0">\n'
    for item in stck:
        print(item)
        html += '<li>%s</li>\n' % item
    html += '</ol>'
    return html

def build_table(cpu):
    return """
<table>
    <tr>
        <th>Register</th>
        <th>Value</th>
    </tr>
    <tr>
        <td>a</th>
        <td>%d</th>
    </tr>
    <tr>
        <td>b</th>
        <td>%d</th>
    </tr>
    <tr>
        <td>c</th>
        <td>%d</th>
    </tr>
    <tr>
        <td>d</th>
        <td>%d</th>
    </tr>
    <tr>
        <td>instruction pointer</th>
        <td>%d</th>
    </tr>
</table>
""" % cpu.get_registers()

def run_program(text):
    program = text.splitlines()
    cpu = VM(program)
    cpu.run()
    return cpu.get_err_string() + "<br>" + build_table(cpu) + "<br>" + build_stack(cpu)

def handle_submit(env, start_response, page):
    body_len = int(env.get("CONTENT_LENGTH", 0))
    body = env["wsgi.input"].read(body_len).decode("UTF-8")
    msg = parse_qs(body).get('message')[0]
    page = build_text_area(msg)
    page += run_program(msg)
    return page

def application(env, start_response):
    page = build_text_area("#insert your code here!")

    if env["REQUEST_METHOD"] == "POST" and env["PATH_INFO"] == '/submit':
        page = handle_submit(env, start_response, page)
    start_response('200 OK', [('Content-Type','text/html')])
    return bytes(page, "UTF-8")
