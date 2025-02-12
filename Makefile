# Makefile for a complex project with node dependencies.
# The dependency relationships are:
#
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
# Running "make all" (or simply "make") will build the following targets:
# n2, n4, n8, n9, n11, n12, n16, n17, n18,
# and Make will build all prerequisites in order.

.PHONY: all clean

# Define a macro for instrumentation:
# It echoes the current time, target name, and shell process ID,
# then executes the given command.
define build_rule
	@echo "[$(shell date +'%T')] Building $@ on PID $$$$"
	@$(1)
endef

# The "all" target builds the following nodes.
all: n4 n2 n8 n9 n11 n12 n16 n17 n18

# n1: no prerequisites.
n1:
	$(call build_rule, touch n1)

# n2 depends on n1.
n2: n1
	$(call build_rule, touch n2)

# n3 depends on n1.
n3: n1
	$(call build_rule, touch n3)

# n4 depends on n3.
n4: n3
	$(call build_rule, touch n4)

# n5 depends on n3.
n5: n3
	$(call build_rule, touch n5)

# n6 depends on n5.
n6: n5
	$(call build_rule, touch n6)

# n7 depends on n5.
n7: n5
	$(call build_rule, touch n7)

# n8 depends on n6.
n8: n6
	$(call build_rule, touch n8)

# n9 depends on n6.
n9: n6
	$(call build_rule, touch n9)

# n13 depends on n3.
n13: n3
	$(call build_rule, touch n13)

# n10 depends on n7, n9, and n13.
n10: n7 n9 n13
	$(call build_rule, touch n10)

# n11 depends on n10.
n11: n10
	$(call build_rule, touch n11)

# n16 depends on n14.
n16: n14
	$(call build_rule, touch n16)

# n12 depends on n11, n10, and n16.
n12: n11 n10 n16
	$(call build_rule, touch n12)

# n14 depends on n13.
n14: n13
	$(call build_rule, touch n14)

# n15 depends on n13.
n15: n13
	$(call build_rule, touch n15)

# n17 depends on n15.
n17: n15
	$(call build_rule, touch n17)

# n18 depends on n12 and n15.
n18: n12 n15
	$(call build_rule, touch n18)

# "clean" target to remove all generated files.
clean:
	@echo "Cleaning up..."
	@rm -f n1 n2 n3 n4 n5 n6 n7 n8 n9 n10 n11 n12 n13 n14 n15 n16 n17 n18

