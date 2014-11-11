#!/usr/bin/env python
import sys
from collections import deque
from math import *
#Ryan Slyter
#CS450
#Programming Assignment: ScapeGoat Tree

#adds all nodes of a tree inorder and returns list of them
def inorder_add(root, array):
   if root is None:
      return   
   inorder_add(root.left, array)
   array.append(root)
   inorder_add(root.right, array)    
   return array

#Converts a sorted array into a weight balanced BST
def array_2_BST(array, start, end):
   if start > end:
      return None

   mid = int(floor((start + end)/2))
   root = array[mid]
   root.left = array_2_BST(array, start, mid-1)
   if root.left is not None:
      root.left.parent = root
   root.right = array_2_BST(array, mid+1, end)
   if root.right is not None:
      root.right.parent = root
   return root

def rebuild_tree(root):
   assert(root is not None)
   array = []
   inorder_array = inorder_add(root, array)
   new_root = array_2_BST(inorder_array, 0, len(inorder_array)-1)
   return new_root

#needs to be called with (tree.root, tree.scapeval, val)
def find_scapegoat(node, sval, x):
   pointer = node
   assert(not(node is None))
   assert(x != node.val) 
   test = sval*size(pointer)
   if test > sval*size(pointer.left) or test > sval*size(pointer.right):
      return pointer #highest scapegoat node
   else:
      if x > pointer.val:
         find_scapegoat(pointer.right, sval, x)
      else:
         find_scapegoat(pointer.left, sval, x)
      
#this can only be called after a new leaf has been inserted
def depth(leaf):
   num = 0
   while leaf is not None:
      num += 1
      leaf = leaf.parent
   return num

def size(root):
   if root is None:
      return 0
   else:
      return size(root.left) + size(root.right) + 1

def tree_min(root):
   pointer = root
   node = pointer 
   while pointer.left is not None:
      node = pointer.left
      pointer = pointer.left
   return node

def successor(root):
   if root.right is not None:
      node = tree_min(root)
      return node
   else:
      pointer = root
      node = pointer.parent
      while node is not None and pointer is node.right:
         pointer = node
         node = node.parent
      return node      

#from slides, replaces one subtree rooted at u with 
#another subtree rooted at v
def transplant(tree, u, v):
   if u.parent is None:
      tree.root = v
   elif u is u.parent.left:
      u.parent.left = v
   else:
      u.parent.right = v
   if v is not None:
      v.parent = u.parent

#Node class for the Scape Goat Tree.
#We'll use parent pointers for inorder prints
#and rebuilding the tree
class Node(object):
   def __init__(self, x):
      self.parent = None
      self.right = None
      self.left = None
      self.val = x

#ScapeGoat tree class itself.
#Note that the tree class itself serves
#as the rootnode through its parent attribute and because
#it holds the scapegoat val.
class Scape_Goat_Tree(object):
   def __init__(self, x, num):
      self.scapeval = x
      self.root = Node(num) #first actual node
      self.max_size = 0
      self.size = 0

#Iterative insert method
   def insert(self, x):
      node = Node(x)
      if self.root is None:
         self.root = node
         self.size+=1
         return
      else:
         pointer = self.root
         previous = None
         while pointer is not None:
            previous = pointer   
            if x > pointer.val:
               pointer = pointer.right
            else:
               pointer = pointer.left
         if x > previous.val:
            previous.right = node
            node.parent = previous
            self.size+=1
            self.max_size = max(self.max_size, self.size)
            test = depth(node)
            #SCAPEGOAT SPECIFIC CODE
            if test > log(self.size, 1/self.scapeval):
              scape_node = find_scapegoat(self.root, self.scapeval, x) 
              #case where scapegoat is the tree root itself 
              if (scape_node is self.root):
                 self.root = rebuild_tree(self.root)
                 self.root.parent = None #hook up
                 self.max_size = self.size
                 return 
              #case where it's not, not an entire tree rebuild
              else:
                 hook = scape_node.parent #hook up
                 if scape_node.parent.right is scape_node:
                    scape_node.parent.right = rebuild_tree(scape_node)
                    scape_node.parent.right.parent = hook #hook up
                    return
                 else:
                    scape_node.parent.left = rebuild_tree(scape_node)
                    scape_node.parent.left.parent = hook #hook up
                    return
            else:
               return #no rebuilding necessary, still weight-balanced 
         else:
            previous.left = node
            node.parent = previous
            self.size+=1
            self.max_size = max(self.max_size, self.size)
            test = depth(node)
            #SCAPEGOT SPECIFIC CODE
            if test > log(self.size, 1/self.scapeval):
               scape_node = find_scapegoat(self.root, self.scapeval, x)
               #case where scapegoat is the tree root itself 
               if (scape_node is self.root):
                  self.root = rebuild_tree(self.root)
                  self.root.parent = None #hook up
                  self.max_size = self.size
                  return 
               #case where it's not, not an entire tree rebuild
               else:
                  hook = scape_node.parent #hook up
                  if scape_node.parent.right is scape_node:
                     scape_node.parent.right = rebuild_tree(scape_node)
                     scape_node.parent.right.parent = hook #hook up     
                     return
                  else:
                     scape_node.parent.left = rebuild_tree(scape_node)
                     scape_node.parent.left.parent = hook #hook up
                     return
            else:
               return               

#Search is the same as any BST
   def search(self, x):
      pointer = self.root
      if pointer is None:
         return 0 #value if value wasn't in tree
      else:
         while pointer != None:
            if x == pointer.val:
               return 1
            elif x > pointer.val:
               pointer = pointer.right
            else:
               pointer = pointer.left
      return 0   

   def delete(self, x):
      pointer = self.root
      if pointer is None:
         return #just return if the val's not there

      #iteratively go down the tree
      while pointer is not None:      
      #Node to delete is actually found
         if x == pointer.val:
            if pointer.left is None:
               transplant(self, pointer, pointer.right)
               self.size-=1
               #TEST AND REBALANCE, ETC
               if self.size <= self.scapeval*self.max_size:
                  self.root=rebuild_tree(self.root)
                  self.root.parent = None
                  self.max_size = self.size
                  return
               return
            elif pointer.right is None:
               transplant(self, pointer, pointer.left)
               self.size-=1
               #TEST AND REBALANCE, ETC
               if self.size <= self.scapeval*self.max_size:
                  self.root=rebuild_tree(self.root)
                  self.root.parent = None
                  self.max_size = self.size
                  return
               return
            else:
               #case where node to delete has two children
               min_node = tree_min(pointer.right)
               if min_node.parent is not pointer:
                  transplant(self, min_node, min_node.right)
                  min_node.right = pointer.right
                  min_node.right.parent = min_node
                  transplant(self, pointer, min_node)
                  min_node.left = pointer.left
                  min_node.left.parent = min_node
                  self.size-=1                  
                  #TEST AND REBALANCE, ETC
                  if self.size <= self.scapeval*self.max_size:
                     self.root=rebuild_tree(self.root)
                     self.root.parent = None
                     self.max_size = self.size
                     return
                  return
               else:
                  transplant(self, pointer, min_node)
                  self.size-=1
                  #TEST AND REBALANCE, ETC
                  if self.size <= self.scapeval*self.max_size:
                     self.root=rebuild_tree(self.root)
                     self.root.parent = None
                     self.max_size = self.size
                     return
                  return
            
            #call delete helper functions here
                             
         elif x > pointer.val:
            pointer = pointer.right                  
         else:
            pointer = pointer.left
      return       
 
   #print function I made to print a tree on its side
   #not as visually effective as treelevels
   def print_tree(self, root, marker):
      if root is None:
         return
      rt_prnt = marker
      self.print_tree(root.left, marker + '-')
      print rt_prnt + ' ' + str(root.val) + '\n'
      self.print_tree(root.right, marker)          
      return

   #class function to print a tree by levels, more effective IMO
   #found this off of leetcode and decided to stick with it during debugging
   def treeLevels(self):
        # Two queues, one for the nodes one for the level of the nodes.
        Q = deque()
        L = deque()
        
        Q.append(self.root)
        level = 0
        L.append(level)
        print level, [self.root.val]

        while len(Q) > 0:
            u = Q.popleft()
            l = L.popleft()

            if u.left != None:
                Q.append(u.left)
                L.append(l + 1)
            if u.right != None:
                Q.append(u.right)
                L.append(l+1)

            #all the nodes in the queue
            #are at the same level, then increment the level and print.
            if len(L) > 0 and L[0] > level and L[0] == L[-1]:
                level += 1
                print level, [x.val for x in Q]



#******************************# MAIN PART OF PROGRAM #********************************#
tree = None
flag = 0

try:
    tree_commands = open("tree.txt", "r") #The pasword file is given to us alrdy
except IOError:        
    sys.exit('Critical: Commands file could not be opened. Program exit.\n')
while (1):
   line = tree_commands.readline()
   if line == '':
      print 'End of file found. Exit.\n'
      break
   parsed = line.split()
   if 'Print' in parsed[0]:
      print 'Result of the Scapegoat tree after finishing file commands up to this point:\n'
      tree.treeLevels()
      continue

   if 'Done' in parsed[0]:
      print 'Done Command Found. Stopped reading file.\n'
      break
   if 'BuildTree' in parsed[0] and flag == 0:
      try:
         scapeval = float(parsed[1])
         initial_node = int(parsed[2])
      except:
         print 'Argument to "BuildTree" in file not correct. Program exit.\n'
         sys.exit(1)
      tree = Scape_Goat_Tree(scapeval, initial_node)
      flag += 1 #prevent from building multiple trees from the file
      continue

   num = int(parsed[1])

   if 'Insert' in parsed[0]:
      tree.insert(num)
   if 'Delete' in parsed[0]:
      tree.delete(num)
   if 'Search' in parsed[0]:
      result = tree.search(num)
      if result == 1:
         print 'Key ' + str(num) + ' was found.\n'
      else:
         print 'Key ' + str(num) + ' was not found.\n'   

tree_commands.close() #close the file
