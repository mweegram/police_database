import tabulate, colorama, sqlite3, datetime

police_force_name = "" # Change This

def colour_print(alert,text,color):
    colorama.init()
    print(f"[{color + alert + colorama.Fore.RESET}] {text}")

class Database:
    def __init__(self):
        self.db = sqlite3.connect('./database.db')
        self.cur = self.db.cursor().execute

        #Table Initialisation
        self.cur('''CREATE TABLE IF NOT EXISTS officers(
                    id INTEGER PRIMARY KEY,
                    firstname TEXT NOT NULL,
                    lastname TEXT NOT NULL,
                    rank INTEGER NOT NULL,
                    department INTEGER NOT NULL,
                    startdate TEXT NOT NULL
                    );''')
        
        self.cur('''CREATE TABLE IF NOT EXISTS ranks(
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    power INTEGER NOT NULL,
                    specific_dept INTEGER
                    );''')
        
        self.cur('''CREATE TABLE IF NOT EXISTS departments(
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                    );''')
        
        self.cur('''CREATE TABLE IF NOT EXISTS trainings(
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT
                    );''')
        
        self.cur('''CREATE TABLE IF NOT EXISTS traininglog(
                    id INTEGER PRIMARY KEY,
                    trainee INTEGER NOT NULL,
                    trainer INTEGER NOT NULL,
                    training INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    date TEXT NOT NULL
                    );''')
        
        self.cur('''CREATE TABLE IF NOT EXISTS comments(
                    id INTEGER PRIMARY KEY,
                    comment TEXT NOT NULL,
                    receiver INTEGER NOT NULL,
                    sender INTEGER NOT NULL,
                    date TEXT NOT NULL
                    );''')
        
        self.db.commit()
    def query_one(self,query,parameters=()):
        result = self.cur(query,parameters).fetchone()
        if result and len(result) == 1:
            result = result[0]
        return result
    def query_all(self,query,parameters=()):
        result = self.cur(query,parameters).fetchall()
        return result
    def insert_one(self,query,parameters):
        self.cur(query,parameters)
        colour_print("Success","Database Insertion Completed Successfully.",colorama.Fore.GREEN)
        self.db.commit()
        return True
    def update_one(self,query,parameters):
        self.cur(query,parameters)
        colour_print("Success","Database Update Successful.",colorama.Fore.GREEN)
        self.db.commit()
        return True
    # Add To The Database
    def insert_new_officer(self,firstname,lastname,rank,department,startdate=datetime.date.today()):
        if not firstname or not lastname or not rank or not department or not startdate:
            colour_print("Failure","Invalid Data Entered.",colorama.Fore.RED)
            return False

        if self.query_one("SELECT 1 FROM officers WHERE firstname = ? AND lastname = ?",(firstname,lastname,)):
            colour_print("Failure","Officer Already Exists With That Name.",colorama.Fore.RED)
            return False
        
        self.insert_one("INSERT INTO officers (firstname,lastname,rank,department,startdate) VALUES (?,?,?,?,?)",(firstname,lastname,rank,department,startdate,))
        return True
    
    def insert_new_rank(self,name,power,dept=None):
        if not name or not power:
            colour_print("Failure","Invalid Data Entered.",colorama.Fore.RED)
            return False
        
        if self.query_one("SELECT 1 FROM ranks WHERE name = ?",(name,)):
            colour_print("Failure","Rank already exists!",colorama.Fore.RED)
            return False

        if not power in range(1,100):
            colour_print("Failure","Invalid Power Amount! Limit: (1-99)",colorama.Fore.RED)
            return False

        self.insert_one("INSERT INTO ranks (name,power,specific_dept) VALUES (?,?,?)",(name,power,dept,))
        return True

    def insert_new_department(self,name):
        if not name:
            colour_print("Failure","Invalid Data Entered.",colorama.Fore.RED)
            return False
        
        if self.query_one("SELECT 1 FROM departments WHERE name = ?",(name,)):
            colour_print("Failure","Department already exists!",colorama.Fore.RED)
            return False
        
        self.insert_one("INSERT INTO departments (name) VALUES (?)",(name,))
        return True
    
    def insert_new_training(self,name,description=None):
        if not name:
            colour_print("Failure","Invalid Data Entered.",colorama.Fore.RED)
            return False
        
        if self.query_one("SELECT 1 FROM trainings WHERE name = ?",(name,)):
            colour_print("Failure","Training With This Name Already Exists.",colorama.Fore.RED)
            return False
        
        self.insert_one("INSERT INTO trainings (name,description) VALUES (?,?)",(name,description,))
        return True

    def insert_new_loggedtraining(self,trainee,trainer,training,status,date=datetime.date.today()):
        if not trainee or not trainer or not training or not status:
            colour_print("Failure","Invalid Data Entered.",colorama.Fore.RED)
            return False
        
        if trainee == trainer:
            colour_print("Failure","Cannot Self-Train!",colorama.Fore.RED)
            return False
        
        if len(self.query_all("SELECT 1 FROM officers WHERE id = ? or id = ?",(trainee, trainer,))) != 2:
            colour_print("Failure","Trainer or Trainee do not exist!",colorama.Fore.RED)
            return False
        
        if not self.query_one("SELECT 1 FROM trainings WHERE id = ?",(training,)):
            colour_print("Failure","Training doesn't exist!",colorama.Fore.RED)
            return False
        
        if self.query_one("SELECT 1 FROM traininglog WHERE trainee = ? AND training = ?",(trainee,training,)):
            colour_print("Failure","Person has or has had this training, please update rather than add new.",colorama.Fore.RED)
            return False
        
        self.insert_one("INSERT INTO traininglog (trainee,trainer,training,status,date) VALUES (?,?,?,?,?)",(trainee,trainer,training,status,date,))
        return True
    
    def insert_new_comment(self,sender,reciever,comment,date=datetime.datetime.now()):
        if not sender or not reciever or not comment:
            colour_print("Failure","Invalid Data Entered.",colorama.Fore.RED)
            return False

        if not len(self.query_all("SELECT 1 FROM officers WHERE id = ? OR id = ?",(sender,reciever,))) == 2:
            colour_print("Failure","Sender or Recipient do not exist!",colorama.Fore.RED)
            return False
        
        self.insert_one("INSERT INTO comments (sender,receiver,comment,date) VALUES (?,?,?,?)",(sender,reciever,comment,date,))
        return True

    #View Database
    def view_all_officers(self):
        officers = self.query_all('''SELECT firstname,lastname,ranks.name,departments.name,startdate 
                                     FROM officers 
                                     INNER JOIN departments ON departments.id = officers.department
                                     INNER JOIN ranks ON ranks.id = officers.rank
                                     ORDER BY power DESC, lastname
                                     ''')
        
        if not officers:
            colour_print("INFO","No Officers Found!",colorama.Fore.BLUE)

        headers = ["Firstname","Surname","Rank","Department","Start Date"]
        print(tabulate.tabulate(officers,headers=headers,tablefmt="psql"))
    
    def view_officer_profile(self,id):
        if not id or not self.query_one("SELECT 1 FROM officers WHERE id = ?",(id,)):
            colour_print("Failure","Invalid ID Enterred.",colorama.Fore.RED)
            return False
        
        officer_details = self.query_one("SELECT officers.id, firstname || ' ' || lastname, ranks.name, departments.name, startdate FROM officers INNER JOIN departments ON departments.id = officers.department INNER JOIN ranks ON ranks.id = officers.rank WHERE officers.id = ?",(id,))
        officer_comments = self.query_all("SELECT comment,officers.firstname || ' ' ||officers.lastname FROM comments INNER JOIN officers ON officers.id = sender WHERE receiver = ?",(id,))
        officer_trainings = self.query_all("SELECT name, status FROM traininglog INNER JOIN trainings ON trainings.id = traininglog.training WHERE trainee = ?",(id,))

        headers = ["ID","Name","Rank","Department","Start Date"]
        print("Officer Details:")
        print(tabulate.tabulate(zip(headers,officer_details),tablefmt="psql"))

        if officer_comments:
            print("Comments:")
            headers = ["Comment","Sender"]
            print(tabulate.tabulate(officer_comments,headers,"psql"))

        if officer_trainings:
            print("Trainings:")
            headers = ["Training Name","Status"]
            print(tabulate.tabulate(officer_trainings,headers,"psql"))

        return True
            
    def view_all_department(self,department):
        if not department or not self.query_one("SELECT 1 FROM departments WHERE id = ?",(department,)):
            colour_print("Failure","Invalid Department Selected.",colorama.Fore.RED)
            return False
        
        dept_officers = self.query_all("SELECT officers.id, firstname || ' ' || lastname, ranks.name from officers INNER JOIN ranks ON ranks.id = officers.rank WHERE department = ? ORDER BY power DESC,lastname",(department,))
        dept_name = self.query_one("SELECT name FROM departments WHERE id = ?",(department,))

        if not dept_officers:
            colour_print("Info","Department is empty.",colorama.Fore.BLUE)
            return False
        
        headers = ["ID","Name","Rank"]
        print(f"\n\n{dept_name}:")
        print(tabulate.tabulate(dept_officers,headers,"psql"))
        return True
    
    # Update Database
    def update_officer_dept(self,officer,new_dept):
        if not officer or not new_dept:
            colour_print("Failure","Invalid Data Entered.",colorama.Fore.RED)
            return False
        
        if not self.query_one("SELECT 1 FROM departments WHERE id = ?",(new_dept,)) or not self.query_one("SELECT 1 FROM officers WHERE id = ?",(officer,)):
            colour_print("Failure","Officer or Department doesn't exist!",colorama.Fore.RED)
            return False

        if self.query_one("SELECT 1 FROM officers WHERE id = ? AND department = ?",(officer,new_dept,)):
            colour_print("Failure","Cannot Update Values, They Are Already Set.",colorama.Fore.RED)
            return False
        
        self.update_one("UPDATE officers SET department = ? WHERE id = ?",(new_dept,officer,))
        return True
    
    def update_officer_rank(self,officer,rank):
        if not officer or not rank:
            colour_print("Failure","Invalid Data Entered.",colorama.Fore.RED)
            return False
        
        if not self.query_one("SELECT 1 FROM officers WHERE id = ?",(officer,)) or not self.query_one("SELECT 1 FROM ranks WHERE id = ?",(rank,)):
            colour_print("Failure","Officer or Rank doesn't exist.",colorama.Fore.RED)
            return False

        if self.query_one("SELECT 1 FROM officers WHERE id = ? AND rank = ?",(officer,rank,)):
            colour_print("Failure","Cannot Update Values, They Are Already Set.",colorama.Fore.RED)
            return False

        self.update_one("UPDATE officers SET rank = ? WHERE id = ?",(rank,officer,))
        return True

    def update_rank_name(self,current,new):
        if not current or not new:
            colour_print("Failure","Invalid Data Entered",colorama.Fore.RED)
            return False
        
        if self.query_one("SELECT 1 FROM ranks WHERE name = ?",(new,)) or not self.query_one("SELECT 1 FROM ranks WHERE name = ?",(current,)):
            colour_print("Failure","Either Rank Doesn't Exist or Rank Exists With The New Name.",colorama.Fore.RED)
            return False

        self.update_one("UPDATE ranks SET name = ? WHERE name = ?",(new,current,))
        return True
    
    def update_rank_power(self,rankid,power):
        if not rankid or not power:
            colour_print("Failure","Invalid Data Entered",colorama.Fore.RED)
            return False
        
        if not self.query_one("SELECT 1 FROM ranks WHERE id = ?",(rankid,)):
            colour_print("Failure","Rank Doesn't Exist!",colorama.Fore.RED)
            return False
        
        if power >= 100 or power <= 0:
            colour_print("Failure","Invalid Power Amount! Limit:(1-99)",colorama.Fore.RED)
            return False
        
        if self.query_one("SELECT 1 FROM ranks WHERE id = ? AND power = ?",(rankid,power,)):
            colour_print("Failure","Data Doesn't Need Update, Values Are The Same As Those Being Set.",colorama.Fore.RED)
            return False

        self.update_one("UPDATE ranks SET power = ? WHERE id = ?",(power,rankid,))
        return True
    
    def update_dept_name(self,deptid,new_name):
        if not deptid or not new_name:
            colour_print("Failure","Invalid Data Entered",colorama.Fore.RED)
            return False
        
        if not self.query_one("SELECT 1 FROM departments WHERE id = ?",(deptid,)) or self.query_one("SELECT 1 FROM departments WHERE name = ?",(new_name,)):
            colour_print("Failure","Department Doesn't Exist or Department With Selected New Name Already Exists!",colorama.Fore.RED)
            return False
        
        self.update_one("UPDATE departments SET name = ? WHERE id = ?",(new_name,deptid,))
        return True
    
    def update_training_status(self,trainee,training,status):
        if not trainee or not training or not status:
            colour_print("Failure","Invalid Data Entered",colorama.Fore.RED)
            return False
        
        if not self.query_one("SELECT 1 FROM traininglog WHERE trainee = ? AND training = ?",(trainee,training,)):
            colour_print("Failure","Officer doesn't have this training.",colorama.Fore.RED)
            return False
        
        if self.query_one("SELECT 1 FROM traininglog WHERE trainee = ? AND training = ? AND status = ?",(trainee,training,status,)):
            colour_print("Failure","New Values Are The Same As Current Values.",colorama.Fore.RED)
            return False

        self.update_one("UPDATE traininglog SET status = ? WHERE trainee = ? AND training = ?",(status,trainee,training,))
        return True
    # Find ID by Name
    def find_officer_id(self,name):
        if not name:
            return False
        
        result = self.query_one("SELECT id FROM officers WHERE firstname || ' ' || lastname LIKE ?",(name,))
        return result
    
    def find_rank_id(self,name):
        if not name:
            return False
        
        result = self.query_one("SELECT id FROM ranks WHERE name LIKE ?",(name,))
        return result
    
    def find_department_id(self,name):
        if not name:
            return False
        
        result = self.query_one("SELECT id FROM departments WHERE name LIKE ?",(name,))
        return result

    def find_training_id(self,name):
        if not name:
            return False
        
        result = self.query_one("SELECT id FROM trainings WHERE name LIKE ?",(name,))
        return result








class Search:
    def __init__(self,database):
        self.selection = ""
        self.db = database
        self.primary_commands = primary_commands = [["insert","select from the insertion features of the database"],
                            ["update","select from the updating features of the database"],
                            ["view  ","select from the view features of the database"],
                            ["exit  ","exit the database"]]
        
        self.secondary_commands = [["officer","rank","department","training","traininglog","comment"],
                              ["department","rank","rankname","rankpower","departmentname","trainingstatus"],
                              ["all","department","profile"],
                              []]
        self.main()
    
    def main(self):
        while self.selection!= "exit":
            self.selection = input(f'({colorama.Fore.BLUE + "Police Database" + colorama.Fore.RESET})> ').lower()
            self.selection = self.selection.split(" ")
            if self.selection == "":
                continue
            elif self.selection[0] == "exit":
                self.selection = "exit"
                colour_print("GOODBYE","Thanks for using the database system.",colorama.Fore.LIGHTMAGENTA_EX)
            elif self.selection[0] == "help":
                self.help_menu()
            elif self.selection[0] == "insert":
                if len(self.selection) == 1:
                    self.selection.append("")
                self.insert_menu(self.selection[1])
            elif self.selection[0] == "update":
                if len(self.selection) == 1:
                    self.selection.append("")
                self.update_menu(self.selection[1])
            elif self.selection[0] == "view":
                if len(self.selection) == 1:
                    self.selection.append("")
                self.view_menu(self.selection[1])
        
        exit()
    def help_menu(self):
        tab      = "    "
        half_tab = "  "
            
        for command in zip(self.primary_commands,self.secondary_commands):
            print(f"{tab*2}{command[0][0]}{tab}{command[0][1]}")
            if command[1]:
                print(f"{tab*3}available commands:")
                for secondary in command[1]:
                    print(f"{tab*3 + half_tab}{secondary}")

    def insert_menu(self,command):
        if not command:
            colour_print("Failure","No Command Supplied!",colorama.Fore.RED)
            return False
        
        if not command in self.secondary_commands[0]:
            colour_print("Failure","Bad Command Supplied!",colorama.Fore.RED)
            return False
        
        pre = f"({colorama.Fore.BLUE + 'Police Database' + colorama.Fore.RESET}) [{colorama.Fore.GREEN + 'insert-'+ command + colorama.Fore.RESET}] "
        if command == "officer":
    
            result = False
            colour_print("INFO","Preparing to add new officer",colorama.Fore.BLUE)
            while result != True:
                firstname = input(pre + "Firstname: ")
                lastname = input(pre + "Lastname: ")
                rank = self.db.find_rank_id(input(pre + "Rank: "))
                department = self.db.find_department_id(input(pre + "Department: "))
                result = self.db.insert_new_officer(firstname,lastname,rank,department)
                if not result:
                    try_again = input("Failed! Try Again (y/n): ").lower()
                    if try_again == "n":
                        return False
                    result = False
        
        elif command == "department":
            result = False
            colour_print("INFO","Preparing to add new department",colorama.Fore.BLUE)
            while result != True:
                name = input(pre + "Department Name: ")
                result = self.db.insert_new_department(name)
                if not result:
                    try_again = input("Failed! Try Again (y/n): ").lower()
                    if try_again == "n":
                        return False
                    result = False  

        elif command == "rank":
            result = False
            colour_print("INFO","Preparing to add new rank",colorama.Fore.BLUE)
            while result != True:
                name = input(pre + "Rank Name: ")
                try:
                    power = int(input(pre + "Power Level (1-99): "))
                except ValueError:
                    colour_print("ERROR","Power value must be integer.",colorama.Fore.RED)
                    continue
                spec_dep = self.db.find_department_id(input(pre + "Department Specific? Leave Blank If Not"))
                result = self.db.insert_new_rank(name,power,spec_dep)
                if not result:
                    try_again = input("Failed! Try Again (y/n): ").lower()
                    if try_again == "n":
                        return False
                    result = False
        
        elif command == "training":
            result = False
            colour_print("INFO","Preparing to add new training course",colorama.Fore.BLUE)
            while result != True:
                name = input(pre + "Training Name: ")
                description = input(pre + "Training Description: ")
                result = self.db.insert_new_training(name,description)
                if not result:
                    try_again = input("Failed! Try Again (y/n): ").lower()
                    if try_again == "n":
                        return False
                    result = False

        elif command == "traininglog":
            result = False
            colour_print("INFO","Preparing to add new training log",colorama.Fore.BLUE)
            while result != True:
                name = self.db.find_training_id(input(pre + "Enter Training Name: "))
                trainer = self.db.find_officer_id(input(pre + "Officer Responsible for Training: "))
                trainee = self.db.find_officer_id(input(pre + "Officer being trained: "))
                status = input(pre + "What was the outcome of training? ")
                result = self.db.insert_new_loggedtraining(trainee,trainer,name,status)
                if not result:
                    try_again = input("Failed! Try Again (y/n): ").lower()
                    if try_again == "n":
                        return False
                    result = False

        elif command == "comment":
            result = False
            colour_print("INFO","Preparing to add new comment",colorama.Fore.BLUE)
            while result != True:
                sender = self.db.find_officer_id(input(pre + "Who is sending the comment: "))
                receiver = self.db.find_officer_id(input(pre + "Who is receiving the comment: "))
                comment = input(pre + "Comment: ")
                result = self.db.insert_new_comment(sender,receiver,comment)
                if not result:
                    try_again = input("Failed! Try Again (y/n): ").lower()
                    if try_again == "n":
                        return False
                    result = False

    def update_menu(self,command):
        if not command:
            colour_print("Failure","No Command Supplied!",colorama.Fore.RED)
            return False

        if not command in self.secondary_commands[1]:
            colour_print("Failure","Bad Command Supplied!",colorama.Fore.RED)
            return False
        
        pre = f"({colorama.Fore.BLUE + 'Police Database' + colorama.Fore.RESET}) [{colorama.Fore.GREEN + 'update-'+ command + colorama.Fore.RESET}] "

        if command == "department":
            result = False
            colour_print("INFO","Preparing to update officer's department",colorama.Fore.BLUE)
            while result != True:
                officer = self.db.find_officer_id(input(pre + "Officer's Name: "))
                department = self.db.find_department_id(input(pre+"New Department: "))
                result = self.db.update_officer_dept(officer,department)
                if not result:
                    try_again = input("Try again? (y/n)").lower()
                    if try_again == "n":
                        return False
                    result = False

        if command == "rank":
            result = False
            colour_print("INFO","Preparing to update officer's department",colorama.Fore.BLUE)
            while result != True:
                officer = self.db.find_officer_id(input(pre + "Officer's Name: "))
                rank = self.db.find_rank_id(input(pre+"New Rank: "))
                result = self.db.update_officer_rank(officer,rank)
                if not result:
                    try_again = input("Try again? (y/n)").lower()
                    if try_again == "n":
                        return False
                    result = False

        if command == "rankpower":
            result = False
            colour_print("INFO","Preparing to update officer's department",colorama.Fore.BLUE)
            while result != True:
                rank = self.db.find_rank_id(input(pre + "Rank's Name: "))
                try:
                    power = int(input(pre+"Rank's New Power (1-99): "))
                except ValueError:
                    colour_print("ERROR","Power Value Must Be Integer between 1-99",colorama.Fore.RED)
                    continue
                result = self.db.update_rank_power(rank,power)
                if not result:
                    try_again = input("Try again? (y/n)").lower()
                    if try_again == "n":
                        return False
                    result = False

        if command == "departmentname":
            result = False
            colour_print("INFO","Preparing to update department name",colorama.Fore.BLUE)
            while result != True:
                department = self.db.find_department_id(input(pre+" Current Department Name: "))
                new_name = input(pre + "New Department Name: ")
                result = self.db.update_dept_name(department,new_name)
                if not result:
                    try_again = input("Try again? (y/n)").lower()
                    if try_again == "n":
                        return False
                    result = False

        if command == "trainingstatus":
            result = False
            colour_print("INFO","Preparing to update training status",colorama.Fore.BLUE)
            while result != True:
                trainee = self.db.find_officer_id(input(pre + "Officer Being Trained Name: "))
                training = self.db.find_training_id(input(pre + "Training Name: "))
                status = input(pre+"New Training Status: ")
                result = self.db.update_training_status(trainee,training,status)
                if not result:
                    try_again = input("Try again? (y/n)").lower()
                    if try_again == "n":
                        return False
                    result = False
        
    def view_menu(self,command):
        if not command:
            colour_print("Failure","No Command Supplied!",colorama.Fore.RED)
            return False

        elif not command in self.secondary_commands[2]:
            colour_print("Failure","Bad Command Supplied!",colorama.Fore.RED)
            return False
        
        pre = f"({colorama.Fore.BLUE + 'Police Database' + colorama.Fore.RESET}) [{colorama.Fore.GREEN + 'update-'+ command + colorama.Fore.RESET}] "

        if command == "all":
            self.db.view_all_officers()

        elif command == "department":
            result = False
            colour_print("INFO","Preparing to show all officers in a selected department",colorama.Fore.BLUE)
            while result != True:
                choice = self.db.find_department_id(input(pre+"Enter Department: "))
                result = self.db.view_all_department(choice)
                if not result:
                    try_again = input("Try Again? (y/n): ")
                    if try_again.lower() != "y":
                        return False
        
        elif command == "profile":
            result = False
            colour_print("INFO","Preparing to show an officers profile",colorama.Fore.BLUE)
            while result != True:
                choice = self.db.find_officer_id(input(pre + "Officer's Name: "))
                result = self.db.view_officer_profile(choice)
                if not result:
                    try_again = input("Try again? (y/n): ")
                    if try_again.lower() != "y":
                        return False


        
