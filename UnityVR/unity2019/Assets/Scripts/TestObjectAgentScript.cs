/**
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using System;
using System.Collections;
using System.Collections.Generic;
using SimpleNetwork;
using UnityEngine;



public class TestObjectAgentScript : AgentScript {

	// Amount already rotated of current rotation
	float totalRotation = 0;

	// Current target rotation
	float targetRotation;

	// Current target position
	Vector3 targetPosition;

	// Is a search currently active
	bool search = true;

	// Controls execution of search
	int searchStep = 0;
	

	/// <summary>
	/// Agent walks the path with smoother turn transitions
	/// </summary>
	bool smoothPath = true;
	
	int gridResX, gridResZ;
	
	Vector3[] pathPoints;


	/// <summary>
	/// Go on with movement
	/// </summary>
	bool goOn = true;

	/// <summary>
	/// Set to true if the agent currently walks along a path
	/// </summary>
	public bool agentIsPathwalking = false;

	/// <summary>
	/// Asynchronous (false) or synchronous (true) mode
	/// </summary>
	protected bool syncMode = false;

	/// <summary>
	/// Agent is moved that much between calls of the Updatefunction - some kind of speed measurement
	/// </summary>	
	public float currentMovementSpeed = 0.0f;
	
	/// <summary>
	/// Maximum speed of agent
	/// </summary>
	protected float movementSpeed = 1.0f;

	/// <summary>
	/// Handle to the script that handles collisions of the agent
	/// </summary>
	protected ControllerCollider controllerColliderScript;

	/// <summary>
	/// The simulation times unit in seconds. Precisely, the time between two send time points of the images. In synchronous mode, 
	/// the sending is always executed in the first frame, therefore it is the simulated time of 2 frames. In asychron mode, we wait at least "SimulationTimePerFrame" seconds
	/// to send an image, hence this is independent of the number of frames passed.
	/// </summary>
	protected float simulationTimePerFrame = 0.1f;

	/// <summary>
	/// Should the agent stop its movement?
	/// </summary>
	public bool movementCanceled = false;


	/// <summary>
	/// Progress of movement: if bigger or equal to GoalDistance, we arrived at the goal position
	/// </summary>
	// protected float DoneDistance = 0F;
	/// <summary>
	/// Set to true if the last movement is done
	/// </summary>
	protected bool isCurrentMovementFinished = true;


	// If Lerpz collides with an object he turns around and contiues the search
	void OnControllerColliderHit(ControllerColliderHit hit){
		if (hit.gameObject.name != "Terrain") {
						targetRotation = 180f;
						searchStep = 1;
				}
	}


	/// <summary>
	/// Movement to a given position
	/// </summary>
	/// <param name="msg">protobuf message</param>
	protected override void ProcessMsgAgentMoveTo(MsgAgentMoveTo msg)
	{	
		GameObject lerpz = GameObject.Find("Lerpz");
		TestObjectBehaviourScript scbs = GameObject.Find("MasterObject").GetComponent<TestObjectBehaviourScript>();
		gridResX = scbs.gridPositions.GetLength(0);
		gridResZ = scbs.gridPositions.GetLength(1);
		
		if (MySimpleNet != null) 
		{
			MySimpleNet.Send (new MsgActionExecutionStatus () {actionID = MovementIDExecuting, status = MsgActionExecutionStatus.InExecution});
		}
		
		// Start and target points of the agents movement
		Vector3 start = lerpz.transform.position;
		Vector3 target = new Vector3(msg.posX, msg.posY, msg.posZ);

		List<int> path = scbs.computePath(start, target);
		if (path != null)
		{
			StartCoroutine(walkPath(path, msg));
		}
		else // No path available
		{
			if (MySimpleNet != null) 
			{
				MySimpleNet.Send (new MsgActionExecutionStatus () {actionID = MovementIDExecuting, status = MsgActionExecutionStatus.Aborted});
			}
		}	
	}



		/// <summary>
	/// Coroutine that lets the agent walk along the given path.
	/// Path is given as a list of grid numbers.
	/// With smoothPath = true: The agent walks and turns at the same time while walking along a bezier curve
	/// With smoothPath = false: For each straight line from one grid position to another the coroutine computes distance and rotation the agent has to travel, turns the agent and calls MovePart().
	/// </summary>
	/// <param name="path">list of grid numbers</param>
	IEnumerator walkPath(List<int> path, MsgAgentMoveTo msg)
	{	
		GameObject lerpz = GameObject.Find("Lerpz");
		TestObjectBehaviourScript scbs = GameObject.Find("MasterObject").GetComponent<TestObjectBehaviourScript>();
		pathPoints = new Vector3[path.Count];
		pathPoints[0] = lerpz.transform.position;
		
		agentIsPathwalking = true;
		
		for (int i = 1; i < path.Count; i++)
		{
			pathPoints[i] = scbs.gridPositions[path[i]%gridResX, path[i]/gridResZ];
			
			if ((msg.targetMode == 1) && (i+1 == path.Count)) // Set last past point to given point if targetMode = 1
			{
				pathPoints[i] = new Vector3(msg.posX, msg.posY, msg.posZ);
			}
			
			pathPoints[i].y = 0f;
			 Debug.DrawLine(pathPoints[i-1], pathPoints[i], Color.blue, 100.0f); // Draws the original (non-bezier) path on the ground		
		}

		if (smoothPath) // Bezier-curved pathwalking
		{	
			if (MySimpleNet != null) 
			{
				MySimpleNet.Send (new MsgActionExecutionStatus () {actionID = MovementIDExecuting, status = MsgActionExecutionStatus.Rotating});
			}
			
			float startingAngle = Vector3.Angle(getBezierPoint(path.Count-1, 0, 0.0001f) - lerpz.transform.position, new Vector3(0f, 0f, 1f));
			if (Vector3.Dot(getBezierPoint(path.Count-1, 0, 0.001f) - lerpz.transform.position, new Vector3(1f, 0f, 0f)) < 0)
			{
				startingAngle = -startingAngle;
			}
			
			goOn = false;
			StartCoroutine(MovePart(startingAngle, 0));
			while (!goOn)
			{
      			yield return null;
			}

			if (MySimpleNet != null) 
			{
				MySimpleNet.Send (new MsgActionExecutionStatus () {actionID = MovementIDExecuting, status = MsgActionExecutionStatus.WalkingRotating});
			}
			
			float angle, dist;
			float t = 0.0f;				  
			float i = 0.0f;
			float pathLength = getPathLength(pathPoints, path.Count);	

			while((t < 1f) && !movementCanceled) 
			{
				yield return new WaitForSeconds(0.01f);
				
				if (syncMode)
				{
					this.CurrentMovementSpeed = this.MovementSpeed * this.SimulationTimePerFrame;
				}
				else
				{
					this.CurrentMovementSpeed = this.MovementSpeed * Time.deltaTime;
				}
				
				i = currentMovementSpeed / pathLength;  
				t += i;
				if (t > 1f)
				{
					t = 1f;
				}
				
				 Debug.DrawLine(lerpz.transform.position, getBezierPoint(path.Count-1, 0, t), Color.red, 100.0f); // Draws a red line of the path walked on the ground
						
				angle = Vector3.Angle(new Vector3(0f,0f,1f), (getBezierPoint(path.Count-1, 0, t)-getBezierPoint(path.Count-1, 0, t-i)));
				if (Vector3.Dot((getBezierPoint(path.Count-1, 0, t-i)-getBezierPoint(path.Count-1, 0, t)), new Vector3(1f,0f,0f)) > 0)
				{
					angle = 360f-angle;
				}
				lerpz.transform.eulerAngles = new Vector3(0f, angle ,0f);
			
				dist = (float)Math.Sqrt((double)((getBezierPoint(path.Count-1, 0, t).x - getBezierPoint(path.Count-1, 0, t-i).x)*(getBezierPoint(path.Count-1, 0, t).x - getBezierPoint(path.Count-1, 0, t-i).x))+
								 					   ((getBezierPoint(path.Count-1, 0, t).z - getBezierPoint(path.Count-1, 0, t-i).z)*(getBezierPoint(path.Count-1, 0, t).z - getBezierPoint(path.Count-1, 0, t-i).z)));
				
				// Actually move the figure and watch out for collisions
				CollisionFlags collisionFlagTemp = MoveAgent (angle, dist);
				
				if (collisionFlagTemp == CollisionFlags.Sides) 
				{
					if (MySimpleNet != null) 
					{		
						MySimpleNet.Send (new MsgCollision () {actionID = this.MovementIDExecuting, colliderID = controllerColliderScript.HitID});
						MySimpleNet.Send (new MsgActionExecutionStatus () {actionID = MovementIDExecuting, status = MsgActionExecutionStatus.Aborted});
					}
					
					this.currentMovementSpeed = 0F; 
					this.isCurrentMovementFinished = true;
					movementCanceled = true;
				} 
				
				// Debug.Log(t); // Outputs the percentage of the path walked
			}	
		}
		else // No bezier-curved pathwalking
		{
			int i = 1;
			float rot = 0, nextRot = 0, dist = 0, currentDist = 0;
		
			while(i+1 < path.Count && !movementCanceled) 
			{	
				rot = Vector3.Angle(pathPoints[i] - pathPoints[i-1], new Vector3(0f, 0f, 1f));
				if (Vector3.Dot(pathPoints[i] - pathPoints[i-1], new Vector3(1f, 0f, 0f)) < 0)
				{
					rot = -rot;
				} 
				nextRot = Vector3.Angle(pathPoints[i+1] - pathPoints[i], new Vector3(0f, 0f, 1f));
				if (Vector3.Dot(pathPoints[i+1] - pathPoints[i], new Vector3(1f, 0f, 0f)) < 0)
				{
					nextRot = -nextRot;
				} 
				
				currentDist = (float)Math.Sqrt((double)((pathPoints[i].x - pathPoints[i-1].x)*(pathPoints[i].x - pathPoints[i-1].x))+
								 					   ((pathPoints[i].z - pathPoints[i-1].z)*(pathPoints[i].z - pathPoints[i-1].z)));
				dist += currentDist;
				if (!(rot == nextRot))
				{
					goOn = false;
					StartCoroutine(MovePart(rot, dist));
					while (!goOn)
					{
		      			yield return null;
					}
					dist = 0;
				}
				
				i++;
			}
			
			currentDist = (float)Math.Sqrt((double)((pathPoints[i].x - pathPoints[i-1].x)*(pathPoints[i].x - pathPoints[i-1].x))+
								 					   ((pathPoints[i].z - pathPoints[i-1].z)*(pathPoints[i].z - pathPoints[i-1].z)));
			dist += currentDist;

			goOn = false;
			StartCoroutine(MovePart(nextRot, dist)); // Last Movement
			while (!goOn)
			{
      			yield return null;
			}
			
		}
		
		if (!movementCanceled) 
		{
			// Set agent to exact desired position
			lerpz.transform.position = pathPoints[path.Count -1];
			
			if (MySimpleNet != null) 
			{
				MySimpleNet.Send (new MsgActionExecutionStatus () {actionID = MovementIDExecuting, status = MsgActionExecutionStatus.Finished});
			}
		}
	
		currentMovementSpeed = 0;
		agentIsPathwalking = false;
	}
	
	/// <summary>
	/// Coroutine that lets the agent turn and then move a part of the complete path, which is walkable without changing direction.
	/// </summary>
	/// <param name="angle">Direction in which the agent has to move</param>
	/// <param name="distance">Distance the agent has to move</param>
	/// <returns></returns>
	IEnumerator MovePart(float angle, float distance)
	{
		GameObject lerpz = GameObject.Find("Lerpz");
		float degree = 0;
		float lerpzAngle = (lerpz.transform.eulerAngles.y)%360;
		if (Math.Abs(angle - lerpzAngle) < 180)
		{
			degree = angle - lerpzAngle;
		}
		else
		{
			if (angle > lerpzAngle)
			{
				degree = (angle - lerpzAngle) - 360;
			}
			else
			{
				degree = (angle - lerpzAngle) + 360;
			}
		}
		
		isCurrentMovementFinished = false;
		
		if (MySimpleNet != null) 
		{
			MySimpleNet.Send (new MsgActionExecutionStatus () {actionID = MovementIDExecuting, status = MsgActionExecutionStatus.Rotating});
		}
		
// Rotation part
		
		Transform t = transform;
		float done = 0.0f;
		float total = Math.Abs(degree);
		float sgn = Math.Sign(degree);
		var startRot = t.eulerAngles;
		float maxSpeed = 30.0f;
		float startSpeedFactor = 0.1f;
		float m = (1.0f - startSpeedFactor) / 0.2f; // slope = delta x / delta y (20%)
		float n2 = 1 + m * 0.8f; // y = mx + n -> n = y - mx
		float speedFactor = 0.5f;
		float donePercent = 0.0f;
		float rot = 0.0f;
		
		// From 0% to 20% accelerate linear
		while ((donePercent < 0.2f) && !movementCanceled)
		{
			speedFactor = startSpeedFactor + m * donePercent;
			rot = speedFactor * maxSpeed * Time.deltaTime;
			t.Rotate(0.0f, sgn * rot, 0.0f);
			done += rot;
			donePercent = done / total;
			yield return null;
		}
		speedFactor = 1.0f;
		
		// From 20% to 80% turn with maximal velocity
		while ((donePercent < 0.8f) && !movementCanceled)
		{
			rot = maxSpeed * Time.deltaTime;
			t.Rotate(0.0f, sgn * rot, 0.0f);
			done += rot;
			donePercent = done / total;
			yield return null;
		}
		
		// From 80% to 100% accelerate negative linear
		while ((donePercent < 1.0f) && !movementCanceled)
		{
			speedFactor = n2 - m * donePercent;
			rot = speedFactor * maxSpeed * Time.deltaTime;
			t.Rotate(0.0f, sgn * rot, 0.0f);
			done += rot;
			donePercent = done / total;
			yield return null;
		}
		
		// Set the rotation angles to desired value
		t.eulerAngles = startRot + new Vector3(0.0f, (degree), 0.0f);
		
		isCurrentMovementFinished = true;
		
// End of rotation part
		
  		while (!isCurrentMovementFinished)
		{
  			 yield return null;
		}
		
		isCurrentMovementFinished = false;
		StartNewMovement(distance, angle);
		while (!isCurrentMovementFinished)
		{
  			 yield return null;
		}

		goOn = true;
	}


	private Vector3 getBezierPoint(int r, int i, float t) 
	{ 
        if(r == 0) 
		{
			return pathPoints[i];
		}

        return (((1 - t) * getBezierPoint(r - 1, i, t)) + (t * getBezierPoint(r - 1, i + 1, t)));
    }


	float getPathLength(Vector3[] pathPoints, int numPoints)
	{
		float length = 0;
		for (int i = 0; i < numPoints-1; i++)
		{
			length += (float)Math.Sqrt((double)((pathPoints[i].x - pathPoints[i+1].x)*(pathPoints[i].x - pathPoints[i+1].x))+
								 			   ((pathPoints[i].z - pathPoints[i+1].z)*(pathPoints[i].z - pathPoints[i+1].z)));	
		}
		return length;
	}
	
}
	