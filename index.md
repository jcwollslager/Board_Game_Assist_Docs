---
layout: page
title: "BG Assist"
permalink: /
---

_"Man does it kind of suck to make board game stuff with Blender. Someone should optimize that."_
- JC, the guy who did that.

Welcome to the BG Assist wiki! Contained in these moderately well documented pages are outlines of every feature of the BG Assist add-on for Blender.

# What is BG Assist?
Board Game Assistant (or BGA, or BG Assist for short), is an add-on for Blender which automates a lot of common steps in making renders and animations for board games. It automates things like generating the geometry for common and uncommon board game components like cards, boxes, dice, and so on, it handles the process of importing and applying your graphics, helps you move components in ways you would on the table such as dropping components onto surfaces and making piles or grids, and on and on.

## How does it work?
Using Blender's add-on system, it runs a bunch of small python scripts in the background to help make the previously mentioned functionality work! As a design principle, most of what it does is meant to run in the background, be easy to undo, and still work even if you uninstall the add-on or share the file with someone who doesn't have it. Many of the tricks it uses are just native Blender features being used in creative ways.

## Why am I here?
In the big picture, no clue. But in terms of this wiki, you're here because you like the idea of making your own stuff in Blender, and I want my clients to come to me for more animations and renders and lighting setups and all that jazz. It's a win-win! By setting up your documents using BGA, not only does it makes it a lot easier for me to work with a wide range of clients from experienced 3D modelers to people using blender for the first time, it also can help you save time and money by not having to rely on me for simple things, like basic renders of basic components.

## Can I use BGA for non-JCW Productions projects?
For your own projects? Absolutely, just a link to my site and credit as "3D Render Pipeline Manager" or whatever you want to call me would be rad. For commercial projects outside of your company, absolutely not. I need the work and, as a reminder, I'm giving this to you for _free_ with the intention of working more with you in the future!

## How do I get in on this?
BGA is only given out to my clients! You'll need:
* to have hired me at some point. Thanks for that, btw. I like having rent and food.
* a license key to maintain updates. I should provide this for you.
* Blender 5.2.2 LTS (it can work on older/newer versions, I don't use extravagant features, but there may be unintended behaviors!)
Once you've gotten all that together, you can follow the installation guide [here!]({{ '/installing/' | relative_url }})

## How'd you make this? I thought you made videos.
I took some comp. sci. classes back in high school and have done hobbyist programming ever since. I actually used to write scripts for After Effects at my old job, and this is just a continuation of that! Blender runs on Python, which is a programming language I know! I'm _relatively_ proficient with it, but to be fully transparent, _a hefty majority of the code is initially AI generated._ This is primarily to help with getting the interface and updates working as intended quickly and efficiently. Then the code is modified and reviewed by me and I test every feature as thoroughly as I can. However, no AI generated imagery or text is used in the making of any other part of this. What you're reading right now is all hand-typed and everything! Lookie that, a robot wouldn't dare write "lookie that."
