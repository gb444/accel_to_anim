# Introduction

This addon is designed for animating space craft, which I've found very hard to animate manually using a conventional keyframe workflow.

The concept is simple. You have your main object who's animation is written to (only in the scene frames range), and an acceleration object that drives it. There's an optional velocity object that can be animated, probably not useful for most use cases but its there to set initial velocities and use as a driver

You then animate the acceleration object (I use constant keyframes to achieve an RCS on/off feel), then bake the animation to the main object.

# How to:
1. In object mode, in the edit panel, select the acceleration object in the panel (I recommend an empty) using the picker
2. Optionally, select a velocity object in the panel
3. Select the object you want the animation to be baked to and press "Setup for active". This will store the links between the 3
4. Animate the acceleration object (don't worry if you've already done this)
5. Press Accel_to_anim
6. Wait
7. Observe your flawless baked animation

# Tips
- The animation is applied in local space, so Z +1 accel means the object will accelerate in its local Z
- The acceleration is scaled by framerate, so +1 Z accel for 1 second will result in an object travelling at 1 U/s
- Baking takes longer than is ideal, so to speed it up, you can restrict the scene frames as you move later in the sequence.


# Install
1. Download as zip
2. Install using the addons preference menu in blender