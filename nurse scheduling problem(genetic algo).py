
if __name__ == '__main__' :
    from tkinter import*
    import tkinter as tk
    root = Tk()
    root.title('nurse scheduling')
    root.geometry("500x400")  # set starting size of window
    root.maxsize(500, 400)  # width x height
    root.config(bg="black")
    import numpy as np
   
    


    # create class 'solution' to make random_schedule then calculate the fitness 'H()' based on hard and soft constraint
    class solution :
        def __init__ ( self , nurse , holidayes_requests ) :
            self.schedule = [ [ ] , [ ] , [ ] , [ ] , [ ] , [ ] , [ ] ]
            self.nurse_num = nurse
            self.holidayes_requests = holidayes_requests
            self.validation = True
            self.Reason = [ ]
            self.conflict = 0
            self.fitness = 0
            self.shifts = [ "M" , "A" , "N" ]
            self.n_shifts_per_day = int ( (self.nurse_num * 5) / 7 )

        def random_schedule ( self ) :
            for i in range ( 7 ) :
                day = [ ]
                nurses_in_day = [ ]
                for j in range ( self.n_shifts_per_day ) :
                    nurse = np.random.randint ( 0 , 100000 ) % self.nurse_num + 1
                    while nurse in nurses_in_day :  # or  (nurse_load[nurse-1] == 3)  and (counter <= self.nurse_num):
                        nurse = np.random.randint ( 1 , self.nurse_num + 1 )
                    nurses_in_day.append ( nurse )
                    element = self.shifts [ j % 3 ] + str ( nurse )
                    day.append ( element )
                self.schedule [ i ] = day

        def working_days_for_nurses ( self ) :
            working_days = [ ]
            # getting all nurses working day in week
            for i in range ( 1 , self.nurse_num + 1 ) :
                nurse = str ( i )
                IN = [ ]
                nurse_shifts = [ self.shifts [ 0 ] + nurse , self.shifts [ 1 ] + nurse , self.shifts [ 2 ] + nurse ]
                p = 0
                for day in self.schedule :
                    p += 1
                    if (nurse_shifts [ 0 ] in day) or (nurse_shifts [ 1 ] in day) or (nurse_shifts [ 2 ] in day) :
                        IN.append ( p )
                working_days.append ( IN )
            return working_days

        def Hard_costrain ( self ) :  # first hard conrtaint chick is all nurses working in range ( 3 : 5 ) day per week
            working_days = self.working_days_for_nurses ( )  # getting working days for all nurses in week
            # working_days is the list has all nurses working days in week
            for i in range ( len ( working_days ) ) :
                if len ( working_days [ i ] ) in range ( 7 , 8 ) :
                    self.validation = False
                    self.Reason.append (
                        str ( len ( working_days [ i ] ) ) + " working day for nurse (" + str ( i + 1 ) + ")" )
                    self.conflict += 1
            # second hard constraint
            # this lines for split the gene into shifts instead days
            new_gene = [ ]
            for day in self.schedule :  # abstract days from gene
                morning = [ ]
                afternoon = [ ]
                night = [ ]
                for j in day :  # abstract shifts from days
                    if self.shifts [ 0 ] in j :
                        morning.append ( j )
                    elif self.shifts [ 1 ] in j :
                        afternoon.append ( j )
                    elif self.shifts [ 2 ] in j :
                        night.append ( j )
                new_gene.append ( morning )
                new_gene.append ( afternoon )
                new_gene.append ( night )
            # discaver (night + morning)shifts conflict
            for i in range ( len ( new_gene ) ) :  # i starting with 1 to 21 note(3 shift per day so 21 shifts per week)
                if (i + 1) % 3 == 0 :  # if (i+1)%3 == 0 this mean the shift is night
                    for j in new_gene [ i ] :  # take all night shifts sequential in one day
                        n = j.replace ( self.shifts [ 2 ] , "" )  # extract nurse in element || delete shift char 'N'
                        for k in new_gene [ (i + 1) % len ( new_gene ) ] :
                            if n in k :
                                self.validation = False
                                self.Reason.append (
                                    "night in day " + str ( int ( i / 3 + 1 ) ) + " are conflict with the morning" )
                                self.conflict += 1

        def calc_fitness ( self ) :
            self.conflict = 0
            self.Reason = [ ]
            self.validation = True

            self.Hard_costrain ( )

            wdays = self.working_days_for_nurses ( )

            if self.conflict == 0 :
                self.fitness = 2
            else :
                self.fitness = round ( 1 / self.conflict , 4 )


    # create class 'Population' to make random different solutions and add new good solutions during Evolution
    class Population :
        def __init__ ( self , n_population , n_nurses , holidayes_requests ) :
            self.parents = [ ]
            self.sub_population = [ ]
            self.size = n_population
            self.n_nurses = n_nurses
            self.holidayes_requests = holidayes_requests

        def new_solution ( self , solution , index ) :
            if index :
                for counter in range ( len ( self.parents ) ) :
                    if solution.schedule == self.parents [ counter ].schedule :
                        return False
            else :
                for counter in range ( len ( self.sub_population ) ) :
                    if solution.schedule == self.sub_population [ counter ].schedule :
                        return False
            return True

        def random_inti_ ( self ) :
            for counter in range ( self.size ) :
                s = solution ( self.n_nurses , self.holidayes_requests )
                s.random_schedule ( )
                while not self.new_solution ( s ,
                                              True ) :  # checking if the schedule is new solution | s:Solution ,True: for searching in first parents list
                    s.random_schedule ( )
                s.calc_fitness ( )
                self.parents.append ( s )
            print ( "population Created" )

        def add ( self , new_parents ) :
            for i in new_parents :
                if self.new_solution ( i , False ) :
                    self.sub_population.append ( i )


    # create the solver class 'genetic_algorithm' to Select best solutions then Recombine and Mutate to find the best of the best solution
    class genetic_algorithm :
        def __init__ ( self , population ) :
            self.population = population
            self.population.sub_population = list ( self.population.parents )
            self.children = [ ]

        # Select best solutions
        def Selection ( self , evolute_growth ) :
            # sort depend on fitnrss
            self.population.sub_population.sort ( key = lambda x : x.fitness , reverse = True )
            # select best of parant
            self.population.sub_population = self.population.sub_population [ 0 :evolute_growth ]
            # taking some of poor parent for taking any good genes from them
            poor_parent = [ ]
            for i in range ( 3 ) :  # 3 will be great
                index = np.random.randint (
                    int ( self.population.size / 3 ) )  # poor parent will be in the third part in population
                poor_parent.append ( self.population.parents [ -index ] )
            self.population.add ( poor_parent )  # using add method for avoid duplication
            return self.population.sub_population [ 0 ]

        # Recombine the best solution to discover new parts on the search space
        def Recombination ( self ) :
            self.children = [ ]
            for par_1 in range ( len ( self.population.sub_population ) ) :
                for par_2 in range ( par_1 + 1 , len ( self.population.sub_population ) , ) :
                    child1 = solution ( self.population.n_nurses , self.population.holidayes_requests )
                    child2 = solution ( self.population.n_nurses , self.population.holidayes_requests )
                    child1.schedule = list ( self.population.sub_population [ par_1 ].schedule )
                    child2.schedule = list ( self.population.sub_population [ par_2 ].schedule )
                    temp = child1.schedule
                    index = np.random.choice ( [ 2 , 3 , 4 ] )
                    child1.schedule [ index : ] = child2.schedule [ index : ]
                    child2.schedule [ index : ] = temp [ index : ]
                    child1.calc_fitness ( )
                    child2.calc_fitness ( )
                    self.children.append ( child1 )
                    self.children.append ( child2 )
            self.children.sort ( key = lambda x : x.fitness , reverse = True )
            self.population.add ( list ( self.children [ :10 ] ) )

        # Mutate the best solution to discover new parts on the search space
        def Mutation ( self ) :
            # swap random day from first part of week with random day from second part of week
            for child in self.children :
                random_day1 = np.random.choice ( [ 0 , 1 , 2 ] )
                random_day2 = np.random.choice ( [ 3 , 4 , 5 , 6 ] )
                child.schedule.insert ( random_day1 , child.schedule.pop ( random_day2 ) )
                child.calc_fitness ( )  # with any changing we must calc_fitness again

            self.children.sort ( key = lambda x : x.fitness , reverse = True )
            # print("child_mutation : ",self.children[0].fitness)
            self.population.add ( list ( self.children [ :10 ] ) )
    
  

    
    # this function to print the final Scedule

    def printing ( x , nurse_size ) :
        half = int(n_nurse / 2)
        weak = [ "sat" , "sun" , "mon" , "tue" , "wed" , "thu" , "fri" ]
        for day in range ( 7 ) :
            print ( "\t\t\t |" + weak [ day ] , end = " " )
        print ( "" )
        for i in range ( 1 , half+1 ) :

            print ( "Nurse " + str ( i ) + " brain:" , end = "    " )
            for j in range ( 7 ) :
                count = 0
                space = 14
                print ( "|" , end = "" )
                for k in x [ j ] :
                    if int ( k [ 1 : ] ) == i :
                        print ( k [ 0 ] , end = " " )
                        count += 1
                        space -= 1
                if count == 0 :
                    print ( "H" , end = "" )
                    count += 1
                for s in range ( space ) :
                    print ( " " , end = "" )
            print ( "" )

        for i in range ( half+1 , nurse_size + 1) :

            print ( "Nurse " + str ( i ) + " heart:" , end = "    " )
            for j in range ( 7 ) :
                count = 0
                space = 14
                print ( "|" , end = "" )
                for k in x [ j ] :
                    if int ( k [ 1 : ] ) == i :
                        print ( k [ 0 ] , end = " " )
                        count += 1
                        space -= 1
                if count == 0 :
                    print ( "H" , end = "" )
                    count += 1
                for s in range ( space ) :
                    print ( " " , end = "" )
            print ( "" )



  
    Label(root, text="Number of nurses", bg="lightgrey").grid(row=1, column=1, padx=5, pady=20, sticky=E)
    Label(root, text="Population Size", bg="lightgrey").grid(row=10, column=1, padx=5, pady=20, sticky=E)
    Label(root, text="Evolution Grows", bg="lightgrey").grid(row=20, column=1, padx=5, pady=20, sticky=E)
    Label(root, text="Evolution loop Size", bg="lightgrey").grid(row=30, column=1, padx=5, pady=20, sticky=E)
    
    name = Entry(root, bd=3)
    name2=Entry(root, bd=3)
    name3=Entry(root, bd=3)
    name4=Entry(root, bd=3)
    def add_nurse() :
        global n_nurse
        global Evolution_precentege
        global size_population
        global loop_size
        
        n_nurse = int(name.get())
        size_population=int(name2.get())
        Evolution_precentege=int(name3.get())
        loop_size=int(name4.get())
        root.destroy()
    submit_nurse_button = Button(root , text="Enter",command=add_nurse).grid(row=50, column=2, padx=30, pady=30, sticky=E)
    
    name.grid(row=1, column=2, padx=5, pady=20)
    name2.grid(row=10, column=2, padx=5, pady=20)
    name3.grid(row=20, column=2, padx=5, pady=20)
    name4.grid(row=30, column=2, padx=5, pady=20)
    
    root.mainloop()


    # taking the number of nurses


    rows , cols = (n_nurse+1 , 7)
    genoTypeList = [ [ 0 for i in range ( cols ) ] for j in range ( rows ) ]



    def editPrinting ( x , nurse_size ) :
        weak = [ "sat" , "sun" , "mon" , "tue" , "wed" , "thu" , "fri" ]
        # for day in range ( 7 ) :
        #     print ( "\t\t\t |" + weak [ day ] , end = " " )
        # print ( "" )
        for i in range ( 1 , nurse_size + 1 ) :
           # print ( "Nurse " + str ( i ) + " :" , end = "    " )
            for j in range ( 7 ) :
                count = 0
                space = 14
                #print ( "|" , end = "" )
                for k in x [ j ] :
                    if int ( k [ 1 : ] ) == i :
                        #print ( k [ 0 ] , end = " " )
                        c=k[0]
                        genoTypeList[i][j]=c
                        count += 1
                        space -= 1
                if count == 0 :
                    #print ( "H" , end = "" )
                    genoTypeList[i][j]="H"
                    count += 1
       




    # taking the holiday request from all nurses
    holidayes_requests = [ ]
    x = 1
    for i in range ( n_nurse ) :
        if x == 0 :
            x = x + 1
        holiday = x
        x = (x + 1) % 8
        while holiday not in range ( 1 , 8 ) :
            holiday = int ( input ( "Enter valid day in range(1:7)day : " ) )
        holidayes_requests.append ( holiday )
    print ( "\t\t\t\t\t-------------------------------" )

    # taking the size of initialization population
    #size_population = int ( input ( "Enter Population Size:" ) )

    # take the best 30% solution for a signing them to genetic algorithm
    #Evolution_precentege = int ( input ( "Evolution Grows:" ) )

    # taking the loop size note(this number is "how much the solver will search for optimal solutions in loop")
   # loop_size = int ( input ( "Evolution loop Size:" ) )

    # create object from population class
    population1 = Population ( size_population , n_nurse , holidayes_requests )
    print ( "Wait for creation...." )

    # initialize random population
    population1.random_inti_ ( )

    print ( "\t\t\t\t\t-------------------------------" )

    # create solver object from genetic algorithm class
    solver = genetic_algorithm ( population1 )

    # select the top10 best sorted solutions
    best_parent = solver.Selection ( Evolution_precentege )

    # poor visialization for waiting
    for i in range ( 0 , loop_size , 10 ) :
        print ( "=" , end = "" )
    print ( "100%" )

    # solver while loop for trying to searching
    while (not (best_parent.fitness > 1)) and (not (loop_size == 0)) :
        solver.Recombination ( )  # crosover all best_parents and get new children
        solver.Mutation ( )  # mutate on all children
        best_parent = solver.Selection (
            Evolution_precentege )  # take the best percentage % from all solution sorted to Evolute
        loop_size -= 1  # loop's increment

        # poor visialization for waiting
        if loop_size % 10 == 0 :
            print ( "#" , end = "" )

    # printing data the final best result
    print ( "\n\t\t\t\t\t  final Solution" ,
            "validation_state :" + str ( best_parent.validation ) ,
            "\t\t fitness :" + str ( best_parent.fitness ) ,
            " confilect number : " + str ( best_parent.conflict ) ,
            "\tthe best Gene :" , best_parent.schedule , sep = "\n" )

    editPrinting ( best_parent.schedule , n_nurse )


    listOfCounters = []
    listOfConHol = []
    
    for i in range ( 1, n_nurse+1 ) :
        maxConhol = 0
        conHol = 0
        Hcounter = 0
        for j in range( 7 ):

            if genoTypeList[i][j] != 'H':
                Hcounter += 1
                conHol = 0
            if genoTypeList[i][j] == 'H':
                conHol += 1
                if conHol > maxConhol:
                    maxConhol = conHol
        if maxConhol !=1:
            listOfConHol.append(maxConhol)
        else:
            listOfConHol.append(0)

        listOfCounters.append( 7 - Hcounter)
    print ( "list of conhol =" , listOfConHol )
    print ( "list of counters = " , listOfCounters )
    print ( "-------------------------\n" )
    maxValinConhol = max ( listOfConHol )
    print("Max number of consctive holidays is "+str(maxValinConhol))
    print ( f'  Nurse number : {listOfConHol.index ( maxValinConhol )+1}' )
    print ( "-------------------------\n" )
    maxValinCounters = max ( listOfCounters )
    print ( "Max number Holidays is " + str(maxValinCounters) )
    print ( f'  Nurse number : {listOfCounters.index ( maxValinCounters )+1}' )
    print ( "-------------------------\n" )
    minValinCounters = min ( listOfCounters )
    print ( "Min number Holidays is " + str ( minValinCounters ) )
    print ( f'  Nurse number : {listOfCounters.index ( minValinCounters ) + 1}' )





    print ( "-------------------------\n" )
    
    
   
    if len ( best_parent.Reason ) != 0 :
        print ( "Conflict Resons :" )
        
        for i in range ( len ( best_parent.Reason ) ) :
            print ( "\t\t\t   " , i + 1 , "- " + str ( best_parent.Reason [ i ] ) )

           
    
    # printing scedule
    print ( "-------------------------\nfinal scedule :" )
    printing ( best_parent.schedule , n_nurse )
    
    
    
    def BB():
        root = Tk()
        root.title('Nurse scheduling')
        root.config(bg="black")
        root.geometry("1000x700")  # set starting size of window
        root.maxsize(8000, 5000)  # width x height
        

        
        T = Text(root, height = 5000, width = 5200)
        

        
        global x 
        global nurse_size
        x=best_parent.schedule
        nurse_size=n_nurse
        T.tag_config('bbk', background="black")
        T.tag_config('warning',  foreground="red",font='Helvetica 18 bold')
        T.tag_config('warning1',  foreground="blue",font='Helvetica 18 bold')
        T.tag_config('warning2',font='Helvetica 18 bold')
        T.insert(tk.END,"validation_state :",'warning1')
        T.insert(tk.END,str ( best_parent.validation ),'warning')
        T.insert(tk.END,"\n")
        T.insert(tk.END,"\nconfilect number :",'warning1')
        T.insert(tk.END,str ( best_parent.conflict ),'warning')
        T.insert(tk.END,"\n")
        T.insert(tk.END,"\nthe best Gene :",'warning1')
        T.insert(tk.END,best_parent.schedule,'warning')
        T.insert(tk.END,"\n")
        T.insert(tk.END,"\nlist of conhol =[",'warning1')
        T.insert(tk.END,listOfConHol,'warning')
        T.insert(tk.END,"]\n")
        T.insert(tk.END,"list of counters = [",'warning1')
        T.insert(tk.END,listOfCounters,'warning')
        T.insert(tk.END,"]\n------------------------------------------------")
        T.insert(tk.END,"\nMax number of consctive holidays is ",'warning1')
        T.insert(tk.END,str(maxValinConhol),'warning')
        T.insert(tk.END,"\n------------------------------------------------")
        T.insert(tk.END,"\nMax number Holidays is ",'warning1')
        T.insert(tk.END,str(maxValinCounters),'warning')
        T.insert(tk.END,"\n------------------------------------------------")
        T.insert(tk.END,"\nMin number Holidays is ",'warning1')
        T.insert(tk.END,str ( minValinCounters ),'warning')
        
        
        T.insert(tk.END,"\n")
        
        if len ( best_parent.Reason ) != 0 :
            
            T.insert(tk.END,"Conflict Resons :",'warning1')
           
            for i in range ( len ( best_parent.Reason ) ) :
                T.insert(tk.END,"\t\t\t   ",'warning')
                T.insert(tk.END,i + 1,'warning')
                T.insert(tk.END,"- ",'warning')
                T.insert(tk.END,str ( best_parent.Reason [ i ] ),'warning')
                T.insert(tk.END,"\n")
                
                

                
        
        
        
        
        
        T.insert(tk.END,"\n\n\n")
        def printing ( x , nurse_size ) :
            half = int(n_nurse / 2)
            weak = [ "sat" , "sun" , "mon" , "tue" , "wed" , "thu" , "fri" ]    
            for day in range ( 7 ) :
                T.insert(tk.END, "\t\t |",'warning2')
                T.insert(tk.END,weak [ day ],'warning2')
                 
            T.insert(tk.END,"\n")
            
            for i in range ( 1 , half+1 ) :

                
                T.insert(tk.END,"Nurse ",'warning2')
                T.insert(tk.END,str ( i ),'warning2')
                T.insert(tk.END," brain:",'warning2')
                
                T.insert(tk.END,'    ')
                
                for j in range ( 7 ) :
                    count = 0
                    space = 14
                    
                    T.insert(tk.END, "|",'warning2')
                 
                   
                    
                    for k in x [ j ] :
                        if int ( k [ 1 : ] ) == i :
                            T.insert(tk.END,k [ 0 ],'warning2')
                           
                            count += 1
                            space -= 1
                    if count == 0 :
                       
                        T.insert(tk.END,"H",'warning2')
                        
                        count += 1
                    for s in range ( space ) :
                   
                        T.insert(tk.END," ",'warning2') 
                        
                T.insert(tk.END,"\n",'warning2')

            for i in range ( half+1 , nurse_size + 1) :

               
                T.insert(tk.END,"Nurse ",'warning2')
                T.insert(tk.END,str ( i ),'warning2')
                T.insert(tk.END," heart:",'warning2')
                T.insert(tk.END,'    ','warning2')
                for j in range ( 7 ) :
                    count = 0
                    space = 14
                    
                    T.insert(tk.END,"|",'warning2')
                    for k in x [ j ] :
                        if int ( k [ 1 : ] ) == i :
                            #print ( k [ 0 ] , end = " " )
                            T.insert(tk.END,k [ 0 ],'warning2')
                            #T.insert(tk.END,'end = " "')
                            count += 1
                            space -= 1
                    if count == 0 :
                        T.insert(tk.END,"H",'warning2')
                        count += 1
                    for s in range ( space ) :

                        T.insert(tk.END," ",'warning2')

                T.insert(tk.END,"\n",'warning2')
                T.pack()
        
        
        printing ( best_parent.schedule , n_nurse )
        
        root.mainloop()

    BB()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    #import pyexcel
    
    # import pyexcel.ext.xls
    #pyexcel.save_as ( array = genoTypeList , dest_file_name = "example.xls" )
    #pyexcel.get_sheet ( file_name = "example.xls" )
    


