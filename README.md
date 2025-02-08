# make_test_demo
Makefile for a complex project with node dependencies.

The dependency relationships are:

#   n1 → n2
#   n1 → n3
#   n3 → n4
#   n3 → n5
#   n5 → n6
#   n5 → n7
#   n6 → n8
#   n6 → n9
#   n7 → n10
#   n9 → n10
#   n13 → n10
#   n10 → n11
#   n11 → n12
#   n10 → n12
#   n16 → n12
#   n12 → n18 
#   n3 → n13
#   n13 → n14
#   n13 → n15
#   n14 → n16
#   n15 → n17
#   n15 → n18
#
Running "make all" (or simply "make") will build the following targets:n2, n4, n8, n9, n11, n12, n16, n17, n18, and Make will build all prerequisites in order.
