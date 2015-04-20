# Updates an XML DOM of a bill and adds attributes for the creation of permalinks to nodes.

import re

def add_permalink_attributes(node, path=[]):
	# Uniquely identify the targettable children of this node. Not
	# all children will be targettable by a permalink (e.g. enum
	# is not targettable.)

	# What children are targettable?
	targets = []
	for child in node:
		get_targets(child, targets)

	# For targets with <enum>, make sure the values are unique.
	# Map all of the enum values to a list of nodes.
	enums = { }
	for child, is_enum, enum_value in targets:
		if is_enum:
			enums.setdefault(enum_value, []).append(child)

	# Now assign permalink attributes to those nodes. When
	# there are duplicates, add extra content to make them
	# unique.
	for enum, nodes in enums.items():
		for i, n in enumerate(nodes):
			if len(nodes) == 1:
				c = enum
			else:
				c = enum + ("~%d" % (i+1))
			p = path + [c]
			n.set('citation-path', "_".join(p))
			add_permalink_attributes(n, p)

	# And assign permalink attributes to other nodes.
	counters = { }
	for child, is_enum, id_prefix in targets:
		if is_enum: continue
		counters[id_prefix] = counters.get(id_prefix, 0) + 1
		p = path + [id_prefix + str(counters[id_prefix])]
		child.set('citation-path', "_".join(p))
		add_permalink_attributes(child, p)

def get_targets(node, targets):
	if node.find("enum") is not None and node.find("enum").text not in (None, ""):
		# If this node has an <enum> child, then this
		# node is targettable.
		targets.append((node, True, re.sub("[^0-9A-Za-z\-]", "", node.find("enum").text)))
	elif node.tag in ("text", "quoted-block"):
		# <text> nodes are targettable.
		targets.append((node, False, "~" + node.tag[0].upper() ))
	else:
		# look for targettable children
		for child in node:
			get_targets(child, targets)


if __name__ == "__main__":
	import sys
	from lxml import etree
	xml_tree = etree.parse(sys.argv[1], etree.XMLParser(recover=True))
	add_permalink_attributes(xml_tree.getroot())
	print(etree.tostring(xml_tree))
