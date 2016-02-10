<h1>Tensegrity Locomotion Research Code</h1>

<h2>Overview</h2>

<h3>Tensegrity Robots</h3>
Tensegrity robots are robots made from solid, rigid struts and springs or springy wires which connect the struts together. The connecting springs attach to the struts at the ends of the struts. A NASA tensegrity robot can be seen below:
![NASA's SUPERball tensegrity robot](https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/NASA_SUPERball_Tensegrity_Lander_Prototype.jpg/311px-NASA_SUPERball_Tensegrity_Lander_Prototype.jpg)
Tensegrities are interesting for a variety of reasons, but most prominently because they are highly mechanically dynamic. Their construction means that they can be expandedor compressed to a significant degree without harming the 
<h3>The Problem</h3>

<h3>The Goal</h3>
The Tensegrity Locomotion Research program aims to implement various ways of providing locomotive capabilities to tensegrity robots by using vibrational motors as the means of movement. The highly vibrationally active nature of tensegrities means that the vibrations induced by these motors can do some pretty funky, unpredictable things. This unpredictability makes it difficult to hard-code functions which are guaranteed to move the robot in the direction or at the speed expected. In order to utilize the tensegrity's high vibrational activity effectively, Prof. John Rieffel and his student assistants have been working to create a program which lets the tensegrity "learn" to move. Whereas one set of movement commands would work for most robots (e.g. motorForward(Motor m) will always move the given motor forward at a set speed), each tensegrity is slightly different, and therefore the effects a certain vibrational frequency has on one is not guaranteed or even expected to have similar effects on another.   

<h3>The Method</h3>
We accomplish this by using a genetic algorithm and implementing a behavioral repertoire, which allow each tensegrity to "learn to walk," so to speak. Initially, each tensegrity must test different combinations of motor frequencies to determine what movement that combination effects. The combination of the set of frequencies used, the movement vector it results in, and the time it takes to traverse that vector for a Beehavior. Once the tensegrity has learned some basic behaviors, it can cpmbine them into more complex behaviors to reach locations the regular behaviors cant. Then we can implement a goal-oriented movement algorithm which selects the most effective behaviors to reach a given location.
 
 <h2>Code Details</h2>
 
 <h3>Code Overview</h3>
 
 <h3>Code Examples</h3>