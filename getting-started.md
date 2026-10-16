---
layout: page
title: Getting Started
permalink: /getting-started/
---

I've been working towards making BGA as accessible as possible. Not for you, but for me, I gotta use it all the time. Let's go through the overview of it! Note that this wiki may get outdated at any time.

# Basic Concepts
## Workflow
Everything about BGA is trying to mimic how you would do the process in real life. As such, the process of working with components is broken down into three main steps: Making a component, Texturing that component, then moving that component around.

### Making Components
Everything in BGA is considered a component, be that the box, the rulebook, the cards, and so on. Just like a rulebook giving you the component list, BGA operates in the same way, where you'll want to group types of components together in order to get the most out of it.

Making a component, be that a card, a chip, a token, a die, a board, or what have you, is done first by picking the size and material. So, for example, if you're making a playing card, you're probably thinking of something poker-sized made from cardstock. Or maybe you're thinking of a wooden meeple that's 20mm tall and 10mm deep. Regardless of what you're making, you always start with the physical aspects to the component.

Using BGA to make the component is going to generate all the texture mapping, physical properties like how it looks when in the light, and most importantly, handle all the geometry and sizing for you. All you have to know is how big your components are going to be, which theoretically you should already know by the time you're here.


### Texturing Components
If making the component was picking out the size, shape, and material, texturing is like printing the graphics onto it. BGA handles all the texture mapping for its components, and is able to handle a variety of organization processes for graphics for things like cards, dice, tokens, boards, boxes, etc.

_However,_ BGA works best if you treat it similarly to how manufacturers print out your board games. You, ideally, want all your graphics on large, combined, single-image grids, grouped by shared components. Think of it like having just one graphics file for every entry in your rulebook's component list. All of one deck of cards gets its own image, all the player boards gets its own image, etc. Now, that doesn't mean you _have_ to have all your component's graphics laid out like that, for the most part BGA is happy to accept individual images, especially as one-offs like the shared back for a deck of cards, though that workflow isn't extensively tested for _every_ card getting its own image. Just keep in mind that the workflow is optimized for grids of images for shared components.

<img alt="Standard Playing Cards Atlas" src="{{ '/assets/images/standard-playing-cards-atlas.png' | relative_url }}" />

_Y'know, something like this. This is also full resolution, so feel free to download this and use it to experiment._

## Component Types
At the highest level, board games are just a bunch of pieces of cardboard, plastic, and metal that are getting moved around on a table. However, there's a lot of overlap between functionality when you _really_ break it down. As such, I refer to things in slightly unusual ways to allow for better shared functionality.

BGA breaks down board game components into these categories:
* **Stackable**
* **Dice**
* **Boxes**
* **Bits**
* **Surfaces**

You might be thinking one of two things: "Only those five?" or "Wow bits must be doing some heavy lifting." Let's get into these categories and explain what each is used for.

### Stackables
What do decks of cards, poker chips, cardboard tokens, coins, and tiles all have in common? That's right. They can be stacked on top of each other. However, that's not at the heart of what makes a stackable a _stackable._

A stackable component is _anything symmetrical that is printed on exactly two sides, shares the same form factor and material, and is often but not always flipped upside-down._ That's it. A deck of cards is no different from a triangular chunky wooden token if you break it down like that. There is a graphic on the top and usually the bottom, sometimes the same, sometimes different, and the side is simply left blank or a solid color with the material it was made out of. When you think about it, like 90% of board game components fall under this category.

When making a stackable component, you start by making just one of them, and you'll typically then turn that singular component into a **Stack.** A stack is a collection of stackable components, with each instance having a variation. So, a standard playing card deck is a stack, with the ace of spades being variation 1, the two of spades being variation 2, and so on, all the way through 52 variations. However, something like the resource cards in catan might have dozens of copies of the same variation, e.g. sheep, wood, etc. Still a stack!

As we've discussed, a deck of cards is a stack. But a scattered pile of tokens? Also a stack. Terrain tiles? Stack. Do multiple players have their own deck of cards? That's alright! Each one can be its own stack even if they all come from the same "pool" of components. Objects that are part of a stack can have stack-like operations done to them, like shuffling their positions, arranging them into grids, making a splay out of them, and so on, so it's worth keeping in mind what is _fundamentally_ a stack, and then work towards the way they're arranged later.

Stack stack stack stack.

### Dice
Contrary to stackables, dice are dice. You know what dice are. Moving on.

### Boxes
Boxes are specifically any containers that you may have. Currently I only have support for the standard two-part board game boxes we all know and love, but eventually I want to incorporate tuckboxes and envelopes, at which point these'll just be named "containers."

### Bits
It's the catch-all! Notably **meeples** are in here, along with cubes, beads, marbles, standees, plastic markers, and basically anything that doesn't fit into any of the other categories. If you struggle to categorize something, it's in here.

### Surfaces
Surfaces, I'll admit, are a bit weird. You'll need to think about them in a similar way to "all squares are rectangles but not all rectangles are squares." We'll start by talking about surfaces like we've talked about other components.

Surfaces, on their own, are things like boards and neoprene mats. They're not typically flipped over, and they're typically low in quantity in your game, usually only having one to four copies of them. Also, they have things put on top of them.

The problem comes from that last bit, "they have things put on top of them," which if you think about it... in a lot of board games, there's a _lot_ of components that have things put on top of them. As a result, _anything can be a surface._ Now when thinking about our surface category, we'll also need to include things like cards that you place cubes onto, tiles that you move pawns on, the insert for the box, the box itself, or even the virtual table that you're posing the components on for renders.

So, that's why _every surface is a component, but not every component is a surface._ You're not regularly placing d4's on top of other d4's, as it were. You'll want to register any component (or non-bga object like tables!) that has things placed on top of it at any point as a surface in BGA to help BGA recognize that things will indeed be put on top of it. Think of the surface category like a standalone expansion with backwards compatibility: you can have a surface on its own, but you can also combine surfaces with stackables to get stackable surfaces, as an example.
