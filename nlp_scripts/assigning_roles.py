# Create the document
message = "let's see that jacket in red and some blue jeans"

# Iterate over parents in parse tree until an item entity is found
def find_parent_item(word):
    # Iterate over the word's ancestors
    for parent in word.ancestors:
        # Check for an "item" entity
        if entity_type(parent) == "item":
            return parent.text
    return None

# For all color entities, find their parent item
def assign_colors(doc):
    # Iterate over the document
    for word in doc:
        # Check for "color" entities
        if entity_type(word) == "color":
            # Find the parent
            parent = find_parent_item(word)
            print("parent: {0} has color : {1}".format(parent, word))

# Assign the colors
doc = nlp(message)
assign_colors(doc)
