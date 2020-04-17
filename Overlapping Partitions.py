import numpy as np
import sys
import time
import random
import operator as op
from functools import reduce
sys.setrecursionlimit(100000)

# N choose R function used to calculate anticipated computational complexity of the dataset
def ncr(n, r):
    r = min(r, n-r)
    numer = reduce(op.mul, range(n, n-r, -1), 1)
    denom = reduce(op.mul, range(1, r+1), 1)
    try:
        return numer / denom
    except OverflowError:
        return 10**150

# Generates individual team pairings
def generate_random_teams(num_players, partition_size):
    players = [i for i in range (1,num_players+1)]
    team1 = random.sample(range(1, num_players+1), partition_size)
    team2 = [i for i in players if i not in team1]
    return team1, team2

# Generates lists of team pairings for the number of weeks inputted by the user
def generate_team_lists(num_players, partition_size, num_weeks):
    t1_list = []
    t2_list = []
    for i in range(num_weeks):
        team1, team2 = generate_random_teams(num_players, partition_size)
        t1_list.append(team1)
        t2_list.append(team2)
    return t1_list, t2_list

# Picks a certain number (10 by default but 50 if computational complexity is anticipated to be high)   
# of random teams and chooses the one with lowest sd to start off on
def generate_starting_team_lists(num_players, partition_size, num_weeks):
    starting_t1_list = []
    starting_t2_list = []
    lowest_sd_starting = 100
    # num_starts is 10 by default but 50 if computational complexity is anticipated to be high
    for i in range(num_starts):
        t1_list, t2_list = generate_team_lists(num_players, partition_size, num_weeks)
        players_matrix = create_matrix(t1_list, t2_list, num_players)
        sd = get_sd(players_matrix)
        if (sd < lowest_sd_starting):
            starting_t1_list = t1_list
            starting_t2_list = t2_list
    return starting_t1_list, starting_t2_list

# Takes list of team pairings and number of players as input and returns the corresponding players matrix
# which stores how often each of the players are together with each other
def create_matrix(t1_list, t2_list, num_players):
    players_matrix = [([0] * num_players) for x in range(num_players)]
    for i in range(len(t1_list)):
        for p in range(partition_size):
            for q in range(partition_size):
                if (p != q):
                    # Converting player numbers to index values in players matrix
                    players_matrix[t1_list[i][p] - 1][t1_list[i][q] - 1] += 1
    for i in range(len(t1_list)):
        for p in range(partition_size2):
            for q in range(partition_size2):
                if (p != q):
                    players_matrix[t2_list[i][p] - 1][t2_list[i][q] - 1] += 1
    return players_matrix

# Updates an existing players_matrix
def update_matrix(players_matrix, removed_t1, removed_t2, added_t1, added_t2):
    for p in range(partition_size):
        for q in range(partition_size):
            if (p != q):
                # converting player numbers to index values in players matrix
                players_matrix[removed_t1[p] - 1][removed_t1[q] - 1] += -1
                players_matrix[added_t1[p] - 1][added_t1[q] - 1] += 1

    for p in range(partition_size2):
        for q in range(partition_size2):
            if (p != q):
                players_matrix[removed_t2[p] - 1][removed_t2[q] - 1] += -1
                players_matrix[added_t2[p] - 1][added_t2[q] - 1] += 1
    return players_matrix

# Prints two teams inputted
def print_teams(t1_list, t2_list):
    print("Teams Pairings:")
    
    for i in range(len(t1_list)):
        print(t1_list[i], t2_list[i], sep="   ")

# Prints matrix inputted
def print_matrix(players_matrix):
    for i in range(len(players_matrix)):
        print(i + 1, ": ", players_matrix[i], sep="")


# Returns a list of the lower diagonal values in the players matrix (discluding zerod diagonal and repeated pairings)
# and gets its standard deviation
def get_sd(players_matrix):
    sample = []
    for i in range(len(players_matrix)):
        for j in range(len(players_matrix)):
            if (i > j):
                if (i != j):
                    sample.append(players_matrix[i][j])
    sd = (np.std(sample))
    return sd

# Sets lowest_sd_global to an arbitrarily large value and initialises counter for number of local minima
lowest_sd_global = 100
counter = 0

# Stores team lists and players matrix corresponding to the current lowest sd
final_t1_list = []
final_t2_list = []
final_players_matrix = []

# Finds local minima values for sd
def find_local_minimum(num_players, t1_list, t2_list, current_sd):
    global lowest_sd_global
    global counter
    global final_t1_list
    global final_t2_list
    global final_players_matrix

    # Updates players matrix
    players_matrix = create_matrix(t1_list, t2_list, num_players)

    # Updates current standard deviation
    current_sd = get_sd(players_matrix)
    
    # Nested for loops find the highest value max_val in the players matrix which corrsponds to the two players that are
    # together the most
    max_val = 0
    for i in range(len(players_matrix)):
        for j in range(len(players_matrix)):
            if (players_matrix[i][j] > max_val):
                highest_i = i
                highest_j = j
                # +1 added as these indeces in order to corrsepond to numerical player values 1,2,3 etc
                highest_vals = [highest_i + 1, highest_j + 1]
                max_val = players_matrix[i][j]
    
    # Finds either 100 local minima or as many can be found in the alotted time
    while (counter < 100 and time.time() < t_end_local_min and lowest_sd_global!= 0):
        
        for j in range(len(players_matrix)):
            # Checks every combination possible involving values on the row of lowest_i that are less than or equal to max_val - 2
            if (players_matrix[highest_i][j] <= max_val - 2 and highest_i != j):
                lowest_vals = [highest_i + 1, j + 1]

                # Checks if there is a team that contains the two values i,j that are together the most and 
                # not the value k whose corresponding [i,k] value in the players matrix >= max_val - 2
                for a in range(len(t1_list)):
                    if ((set(highest_vals).issubset(t1_list[a]) and ((set(lowest_vals).issubset(t1_list[a])) == False))
                            or (set(highest_vals).issubset(t2_list[a]) and ((set(lowest_vals).issubset(t2_list[a])) == False))):
                        
                        # Checks if the two values that are together the most are a part of team1
                        if (set(highest_vals).issubset(t1_list[a])):
                            
                            # potential_lowering function returns the potential sd of the players_matrix that swapping these 
                            # two values would bring
                            potential_sd, t1_list, t2_list, players_matrix = potential_lowering(t1_list, t2_list, t1_list[a],
                                                                                 t2_list[a], highest_vals[1], lowest_vals[1],
                                                                                 players_matrix)
                            
                            # Checks to find if neighbouring value brings down the sd and if so makes the swap
                            if (potential_sd < current_sd):
                                
                                t1_list[a].remove(highest_vals[1])
                                t1_list[a].append(lowest_vals[1])

                                t2_list[a].remove(lowest_vals[1])
                                t2_list[a].append(highest_vals[1])
                                
                                # Runs function again with new player matrix and team lists to find neighbouring value to these values that brings down the sd
                                find_local_minimum(num_players, t1_list, t2_list, potential_sd)
                        
                        # Otherwise the two values that are together the most are a part of team2
                        else:
                            potential_sd, t1_list, t2_list, players_matrix = potential_lowering(t1_list, t2_list, t1_list[a],
                                                                                     t2_list[a], lowest_vals[1], highest_vals[1],
                                                                                 players_matrix)
                            
                            # Checks if this neighbouring value brings down the sd and if not returns to the top of the for loop
                            if (potential_sd < current_sd):
            
                                t2_list[a].remove(highest_vals[1])
                                t2_list[a].append(lowest_vals[1])
                                
                                t1_list[a].remove(lowest_vals[1])
                                t1_list[a].append(highest_vals[1])
                                
                                # Runs function again with new player matrix and team lists to find neighbouring value to these values that brings down the sd
                                find_local_minimum(num_players, t1_list, t2_list, current_sd)

        # Called if algorithm couldn't lower sd by swapping two players from one team to another (i.e. no neighbours are lower, 
        # local minimum found)
        print("Local sd minimum: ", current_sd)

        if (current_sd < lowest_sd_global):
            lowest_sd_global = current_sd
    
            final_t1_list = t1_list
            final_t2_list = t2_list
            final_players_matrix = players_matrix

        # Try again fresh to find a new local minimum to see if the globabl minimum can be found
        counter += 1
        
        # Generates new random set of teams to effectively start at some other partially optimized random point in the graph
        t1_list1, t2_list1 = generate_starting_team_lists(num_players, partition_size, num_weeks)
        find_local_minimum(num_players, t1_list1, t2_list1, 100)
    
    # Called if while loop couldn't find local minimum within allotted time because of computational complexity
    print("Local sd minimum: ", current_sd)
    
    if (current_sd < lowest_sd_global):
        lowest_sd_global = current_sd

        final_t1_list = t1_list
        final_t2_list = t2_list
        final_players_matrix = players_matrix
        
    #####################################################################################################################
    # After absolute lowest sd has been found
    
    # Generates initial starting order for minimize_overlap function
    final_t1_list, final_t2_list = generate_starting_order(final_t1_list, final_t2_list)
    
    
    # Overlap matrix stores overlap each of the team pairings have with each of the other team pairings
    overlap_matrix = [([0] * len(t1_list)) for x in range(len(t1_list))]
    # Gets smallest overlap as this part of the code will only be called once and only needs to be excecuted once so it won't be calculated on every recursion of 
    # the minimize_overlap function
    smallest_overlap = 100
    # Returns smallest overlap
    for i in range(len(t1_list)):
        for j in range(len(t1_list)):
                if(i!=j):
                    overlap_matrix[i][j] = max(len(set(t1_list[i]).intersection(set(t1_list[j])))/partition_size , len(set(t1_list[i]).intersection(set(t2_list[j])))/partition_size2)
                    if (overlap_matrix[i][j] < smallest_overlap):
                        smallest_overlap = overlap_matrix[i][j]
    print("Minimum Possible Overlap:", smallest_overlap)                  
    # Alots a maximum amount of time to minimize overlap
    overlap_end_time = time.time() + (0.25 * max_time)
    final_t1_list_ordered, final_t2_list_ordered, sequence_average_overlap = minimize_overlap(final_t1_list , final_t2_list, overlap_end_time, smallest_overlap)
    
    # Prints results
    print("\nIdeal order for teams:")
    print_teams(final_t1_list_ordered, final_t2_list_ordered)
    print("\nIdeal players matrix:")
    print_matrix(final_players_matrix)  
    print("\nAbsolute Lowest sd: ", lowest_sd_global)
    print("\nAverage overlap: ", round(sequence_average_overlap,6))
    end = time.time()
    print("\nThe programme took", end - start, "seconds to complete.")
    
    sys.exit()

def potential_lowering(t1_list, t2_list, team1, team2, team1_val_remov, team1_val_add, players_matrix):
    # Sets these values to tuple lists to make them immutable and not change
    old_t1_list = [tuple(l) for l in t1_list]
    old_t2_list = [tuple(l) for l in t2_list]
    old_players_matrix = [tuple(l) for l in players_matrix]
    
    # Swaps potential elements
    t1_index = t1_list.index(team1)
    t2_index = t2_list.index(team2)
    
    # Makes potential teams to be added
    t1_list[t1_index].remove(team1_val_remov)
    t1_list[t1_index].append(team1_val_add)
    t2_list[t2_index].remove(team1_val_add)
    t2_list[t2_index].append(team1_val_remov)
    
    # Converts old_t1_list back to list of lists now that the changing of values has happened
    old_t1_list = [list(l) for l in old_t1_list]
    old_t2_list = [list(l) for l in old_t2_list]
    
    # Defines removed teams and added teams
    removed_t1 = old_t1_list[t1_index]
    removed_t2 = old_t2_list[t2_index]
    added_t1 = t1_list[t1_index]
    added_t2 = t2_list[t2_index]
    
    
    # Calculates potential players matrix and sd from lowering those elements
    players_matrix = update_matrix(players_matrix, removed_t1, removed_t2, added_t1, added_t2)
    sd = get_sd(players_matrix)
    
    # Converts old_players_matrix back to list of lists now that the changing of values has happened
    old_players_matrix = [list(l) for l in old_players_matrix]
    
    return sd, old_t1_list, old_t2_list, old_players_matrix


def average_overlap(t1_list, t2_list):
    
    overlaps = []
    
    # average overlap = max{|Ai+1 ∩Ai|,|Ai+1 ∩([n]−Ai|}
    for i in range(len(t1_list) - 1):
        overlaps.append(max(len(set(t1_list[i]).intersection(set(t1_list[i+1])))/partition_size , len(set(t1_list[i]).intersection(set(t2_list[i+1])))/partition_size2))
    
    # Calculates overlap between last value and first value to take repeating into account
    overlaps.append(max(len(set(t1_list[len(t1_list) - 1]).intersection(set(t1_list[0])))/partition_size , len(set(t1_list[len(t1_list) - 1]).intersection(set(t2_list[0])))/partition_size2))
    average_overlap = sum(overlaps)/(len(t1_list))
    return average_overlap, overlaps

def generate_starting_order(t1_list, t2_list):
    starting_t1_list = []
    starting_t2_list = []
    lowest_overlap = 100
    # Scans the space by taking a certain number random team lists depending on complexity and starting with the lowest
    # average overlap value of team lists
    for i in range(num_starts):
        shuffled_lists = list(zip(t1_list, t2_list))
        random.shuffle(shuffled_lists)
        t1_list, t2_list = zip(*shuffled_lists)
        t1_list = [list(l) for l in t1_list]
        t2_list = [list(l) for l in t2_list]
        average_seq_overlap, a = average_overlap(t1_list,t2_list)
        
        if (average_seq_overlap < lowest_overlap):
            starting_t1_list = t1_list
            starting_t2_list = t2_list
            lowest_overlap = average_seq_overlap
    
    return starting_t1_list, starting_t2_list
    
global_lowest_overlap = 100
ideal_t1_list_ordered = []
ideal_t2_list_ordered = []
counter2 = 0
    
def minimize_overlap(t1_list, t2_list, overlap_end_time, smallest_overlap):
    global ideal_t1_list_ordered
    global ideal_t2_list_ordered
    global global_lowest_overlap
    global counter2

    current_average_overlap, overlaps = average_overlap(t1_list,t2_list)
    
    # Overlap matrix stores overlap each of the team pairings have with each of the other team pairings
    overlap_matrix = [([0] * len(t1_list)) for x in range(len(t1_list))]
    sequence_list = [i for i in range (len(t1_list))]
    sequence_list = [x for _,x in sorted(zip(overlaps,sequence_list))]
    
    # Reverses sequence list so that the greatest overlaps will be listed first
    sequence_list.reverse()
      
    # Generates overlap matrix
    for i in range(len(t1_list)):
        for j in range(len(t1_list)):
                if(i!=j):
                    overlap_matrix[i][j] = max(len(set(t1_list[i]).intersection(set(t1_list[j])))/partition_size , len(set(t1_list[i]).intersection(set(t2_list[j])))/partition_size2)
     
    # If the current minimum is lower than the global overlap it is set to equal it
    if (current_average_overlap < global_lowest_overlap):
        global_lowest_overlap = current_average_overlap
        ideal_t1_list_ordered = t1_list
        ideal_t2_list_ordered = t2_list
            
    
    # Gets 10 local minima or as many as can be gotten in the time limit
    while(time.time() < overlap_end_time and round(current_average_overlap,6)  != round(smallest_overlap,6)):
        for i in range (len(t1_list)-1):
            if (round(overlap_matrix[i][i+1],3) > round(smallest_overlap,3)):
                for j in sequence_list:
                    if(i != j):
                        
                        
                        # Catchall statement in case programme is stuck in this for loop
                        if(time.time() > overlap_end_time):
                            if (current_average_overlap < global_lowest_overlap):
                                global_lowest_overlap = current_average_overlap
                                ideal_t1_list_ordered = t1_list
                                ideal_t2_list_ordered = t2_list
                            return ideal_t1_list_ordered, ideal_t2_list_ordered, global_lowest_overlap
                        
                        
                        # Swaps i and j and checks if this lowers the average overlap in a similar way to the checking for lower sd done above
                        t2_list[i], t2_list[j] = t2_list[j], t2_list[i]
                        t1_list[i], t1_list[j] = t1_list[j], t1_list[i]
                        
                        new_average_overlap, a = average_overlap(t1_list,t2_list)
                        if (new_average_overlap < current_average_overlap):
                            
                            current_average_overlap = new_average_overlap
    
                            minimize_overlap(t1_list, t2_list, overlap_end_time, smallest_overlap)
                            
                        else:
                            # Swap back if it doesn't lower average overlap
                            t2_list[i], t2_list[j] = t2_list[j], t2_list[i]
                            t1_list[i], t1_list[j] = t1_list[j], t1_list[i]
                            
    
        # If the current minimum is lower than the global overlap it is set to equal it
        if (current_average_overlap < global_lowest_overlap):
            global_lowest_overlap = current_average_overlap
            ideal_t1_list_ordered = t1_list
            ideal_t2_list_ordered = t2_list
        
        print("local overlap minimium:", current_average_overlap)
        
        # Catchall if average_overlap can no longer be lowered because all overlap values = minimum overlap
        if(round(current_average_overlap,6)  == round(smallest_overlap,6)):
            return ideal_t1_list_ordered, ideal_t2_list_ordered, global_lowest_overlap
        counter2 +=1
        
        # Starts again with the teams in a new random order
        t1_list, t2_list = generate_starting_order(t1_list, t2_list)
        
        minimize_overlap(t1_list, t2_list, overlap_end_time, smallest_overlap)
    return ideal_t1_list_ordered, ideal_t2_list_ordered, global_lowest_overlap
    
num_players = int(input("Enter total number of players: "))
partition_size = int(input("Enter partition size: "))
num_weeks = int(input("Enter number of weeks: "))
max_time = int(input("Enter a maximum amount of time you would like the programme to take (in seconds) that is greater than 30 seconds: "))
if(max_time < 30):
    max_time = 30

start = time.time()

# Chooses 10 random values by default but if computational complexity is deemed to be too high
# to return more than a handful of local minima and the space to be explored is very large. It explores
# the space more thoroughly(by picking the best of 50 random starting points) before commencing 
# perfecting the lists
possible_num_combos = ncr(num_players, partition_size)
comp_complexity = ncr(int(possible_num_combos), num_weeks)

if (comp_complexity >= 10**150):
    num_starts = 50
else:
    num_starts = 10

    
partition_size2 = num_players - partition_size

t1_list1, t2_list1 = generate_team_lists(num_players, partition_size, num_weeks)
        
# Gives a maximum time to find local minima
t_end_local_min = time.time() + (0.7 * max_time)
find_local_minimum(num_players, t1_list1, t2_list1, 100)