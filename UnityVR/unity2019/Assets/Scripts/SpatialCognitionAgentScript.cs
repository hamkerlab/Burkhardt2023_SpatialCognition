/**
@brief Overloaded control class for an agent performing several spatial cognition tasks

@details
 - Derived from AgentScript
 - Implements the pathwalking message and the logic behind it
 - Intended to be used with the "SpatialCognition" scene

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System;
using System.Linq;
using SimpleNetwork;
using UnityEngine.AI;

public class SpatialCognitionAgentScript : AgentScript
{	 
    bool goOn = true; // Go on with movement
    bool smoothPath = true; // Smooth A* path
    bool agentIsPathwalking = false;
    int gridResX, gridResZ;

    Vector3 start;
    Vector3 target;
    Vector3 lastStopPosition;
    
    Vector3[] pathPoints;

    /// <summary>
    /// Movement to a given position
    /// </summary>
    /// <param name="msg">protobuf message</param>
    protected override void ProcessMsgAgentMoveTo(MsgAgentMoveTo msg)
    {
        GameObject felice = GameObject.Find("felice_grasp");
        SpatialCognitionBehaviourScript scbs = GameObject.Find("MasterObject").GetComponent<SpatialCognitionBehaviourScript>();
        gridResX = scbs.gridPositions.GetLength(0);
        gridResZ = scbs.gridPositions.GetLength(1);

        if (MySimpleNet != null)
        {
            MySimpleNet.Send(new SimpleNetwork.MsgActionExecutionStatus() { actionID = this.MovementIDExecuting, status = SimpleNetwork.MsgActionExecutionStatus.InExecution });
        }

        //mibur: new pathwalking coroutine with navmesh AI pathwalking
		StartCoroutine(walkingRoutine(msg));
    }

    private Vector3 getBezierPoint(int r, int i, float t)
    {
        if (r == 0)
        {
            return pathPoints[i];
        }

        return (((1 - t) * getBezierPoint(r - 1, i, t)) + (t * getBezierPoint(r - 1, i + 1, t)));
    }

    float getPathLength(Vector3[] pathPoints, int numPoints)
    {
        float length = 0;
        for (int i = 0; i < numPoints - 1; i++)
        {
            length += (float)Math.Sqrt((double)((pathPoints[i].x - pathPoints[i + 1].x) * (pathPoints[i].x - pathPoints[i + 1].x)) +
                                               ((pathPoints[i].z - pathPoints[i + 1].z) * (pathPoints[i].z - pathPoints[i + 1].z)));
        }
        return length;
    }
	
	/// mibur: NEW coroutine that lets the agent walk along the given path using the Unity navmesh AI pathwalking
    IEnumerator walkingRoutine(MsgAgentMoveTo msg)
    {
        GameObject felice = GameObject.Find("felice_grasp");
        SpatialCognitionBehaviourScript scbs = GameObject.Find("MasterObject").GetComponent<SpatialCognitionBehaviourScript>();

        start = felice.transform.position;
        target = new Vector3(msg.posX, msg.posY, msg.posZ);
        lastStopPosition = start;

        float stepSize = 0.07f;  // size of each step when running in sync mode

        this.CurrentMovementSpeed = 1f;
        agentIsPathwalking = true;
        agent.SetDestination(target);

        // Send "walk started" network message
        if (MySimpleNet != null)
        {
            MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = this.MovementIDExecuting, status = MsgActionExecutionStatus.WalkingRotating });
        }

        // get the path
        NavMeshPath path = new NavMeshPath();
        if (!agent.CalculatePath(target, path))
        {
            Debug.LogError("Could not calculate path");
            yield break;
        }

        int currentCorner = 0;

        // main movement loop
        while (currentCorner < path.corners.Length)
        {
            Vector3 nextTarget = path.corners[currentCorner];

            while (currentCorner < path.corners.Length)
            {
                nextTarget = path.corners[currentCorner];

                while ((agent.transform.position - nextTarget).sqrMagnitude > stepSize * stepSize)
                {
                    if (makeVideo)
                    {
                        // Calculate the direction and the next step
                        Vector3 direction = (nextTarget - agent.transform.position).normalized;
                        Vector3 nextStep = agent.transform.position + direction * stepSize;

                        // Check if the next step is closer to the target
                        if ((nextStep - nextTarget).sqrMagnitude > (agent.transform.position - nextTarget).sqrMagnitude)
                        {
                            // If it's not, move the agent directly to the target
                            nextStep = nextTarget;
                        }

                        // Calculate the angle between the agent's current forward direction and the direction to the next step
                        float angle = Vector3.Angle(agent.transform.forward, direction);

                        // Reduce the step size if the agent has to turn a large amount
                        if (angle > 15f) // adjust this value as needed
                        {
                            nextStep = agent.transform.position + direction * stepSize * 0.8f; // adjust this value as needed
                        }

                        // Stop the agent
                        agent.isStopped = true;

                         // Update agent's rotation to face towards the next step
                        Quaternion toRotation = Quaternion.LookRotation(direction, Vector3.up);
                        agent.transform.rotation = Quaternion.Slerp(agent.transform.rotation, toRotation, Time.deltaTime * 10f);

                        // Wait for a message from SimpleNet to continue
                        while (!syncContinue)
                        {
                            yield return null;
                        }

                        // Resume the agent
                        agent.isStopped = false;
                        syncContinue = false;  // Reset syncContinue

                        // Check if the next step is on the NavMesh
                        NavMeshHit hit;
                        if (NavMesh.SamplePosition(nextStep, out hit, stepSize, NavMesh.AllAreas))
                        {
                            // Move the agent to the next step
                            agent.transform.position = nextStep;

                            // Update the last stop position
                            lastStopPosition = agent.transform.position;
                        }
                    }

                    // Suspend execution until the next frame
                    yield return null;
                }

                currentCorner++;
            }
        }

        // Send "walk completed" network message
        if (MySimpleNet != null)
        {
            MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = this.MovementIDExecuting, status = MsgActionExecutionStatus.Finished });
        }

        this.CurrentMovementSpeed = 0.0f;
        agentIsPathwalking = false;
        Debug.Log("Walk finished");
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
        GameObject felice = GameObject.Find("felice_grasp");
        SpatialCognitionBehaviourScript scbs = GameObject.Find("MasterObject").GetComponent<SpatialCognitionBehaviourScript>();
        pathPoints = new Vector3[path.Count];
        pathPoints[0] = felice.transform.position;

        agentIsPathwalking = true;

        for (int i = 1; i < path.Count; i++)
        {
            pathPoints[i] = scbs.gridPositions[path[i] % gridResX, path[i] / gridResZ];

            if ((msg.targetMode == 1) && (i + 1 == path.Count)) // Set last past point to given point if targetMode = 1
            {
                pathPoints[i] = new Vector3(msg.posX, msg.posY, msg.posZ);
            }

            pathPoints[i].y = 0f;
            Debug.DrawLine(pathPoints[i - 1], pathPoints[i], Color.blue, 100.0f); // Draws the original (non-bezier) path on the ground		
        }

        if (smoothPath) // Bezier-curved pathwalking
        {
            if (MySimpleNet != null)
            {
                MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = this.MovementIDExecuting, status = MsgActionExecutionStatus.Rotating });
            }

			//float startingAngle = Vector3.Angle(getBezierPoint(path.Count - 1, 0, 0.0001f) - felice.transform.position, new Vector3(0f, 0f, 1f));
			//To compute the starting angle we only need the vector between felice and the first path point. getBezierPoint seems to calculate some kind of average direction of the path which makes the turn look bad
			float startingAngle = Vector3.Angle(pathPoints[1] - felice.transform.position, new Vector3(0f, 0f, 1f));
		
            if (Vector3.Dot(getBezierPoint(path.Count - 1, 0, 0.001f) - felice.transform.position, new Vector3(1f, 0f, 0f)) < 0)
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
                MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = this.MovementIDExecuting, status = MsgActionExecutionStatus.WalkingRotating });
            }

            float angle, dist;
            float t = 0.0f;
            float i = 0.0f;
            float pathLength = getPathLength(pathPoints, path.Count);

            while ((t < 1f) && !movementCanceled)
            {
                yield return new WaitForSeconds(0.01f);

                if (SyncMode)
                {
                    this.CurrentMovementSpeed = this.MovementSpeed * this.SimulationTimePerFrame;
                }
                else
                {
                    this.CurrentMovementSpeed = this.MovementSpeed * Time.deltaTime;
                }

                i = this.CurrentMovementSpeed / pathLength;
                t += i;
                if (t > 1f)
                {
                    t = 1f;
                }

                Debug.DrawLine(felice.transform.position, getBezierPoint(path.Count - 1, 0, t), Color.red, 100.0f); // Draws a red line of the path walked on the ground

                angle = Vector3.Angle(new Vector3(0f, 0f, 1f), (getBezierPoint(path.Count - 1, 0, t) - getBezierPoint(path.Count - 1, 0, t - i)));
                if (Vector3.Dot((getBezierPoint(path.Count - 1, 0, t - i) - getBezierPoint(path.Count - 1, 0, t)), new Vector3(1f, 0f, 0f)) > 0)
                {
                    angle = 360f - angle;
                }
                felice.transform.eulerAngles = new Vector3(0f, angle, 0f);

                dist = (float)Math.Sqrt((double)((getBezierPoint(path.Count - 1, 0, t).x - getBezierPoint(path.Count - 1, 0, t - i).x) * (getBezierPoint(path.Count - 1, 0, t).x - getBezierPoint(path.Count - 1, 0, t - i).x)) +
                                                       ((getBezierPoint(path.Count - 1, 0, t).z - getBezierPoint(path.Count - 1, 0, t - i).z) * (getBezierPoint(path.Count - 1, 0, t).z - getBezierPoint(path.Count - 1, 0, t - i).z)));

                // Actually move the figure and watch out for collisions
                CollisionFlags collisionFlagTemp = MoveAgent(angle, dist);
				/*
                if (collisionFlagTemp == CollisionFlags.Sides)
                {
                    Debug.Log("Collided with an object???");
                    if (MySimpleNet != null)
                    {
                        MySimpleNet.Send(new MsgCollision() { actionID = this.MovementIDExecuting, colliderID = ControllerColliderScript.HitID });
                        MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = this.MovementIDExecuting, status = MsgActionExecutionStatus.Aborted });
                    }

                    this.CurrentMovementSpeed = 0F;
                    this.IsCurrentMovementFinished = true;
                    movementCanceled = true;
                }
				 */
                // Debug.Log(t); // Outputs the percentage of the path walked
            }
        }
        else // No bezier-curved pathwalking
        {
            int i = 1;
            float rot = 0, nextRot = 0, dist = 0, currentDist = 0;

            while (i + 1 < path.Count && !movementCanceled)
            {
                rot = Vector3.Angle(pathPoints[i] - pathPoints[i - 1], new Vector3(0f, 0f, 1f));
                if (Vector3.Dot(pathPoints[i] - pathPoints[i - 1], new Vector3(1f, 0f, 0f)) < 0)
                {
                    rot = -rot;
                }
                nextRot = Vector3.Angle(pathPoints[i + 1] - pathPoints[i], new Vector3(0f, 0f, 1f));
                if (Vector3.Dot(pathPoints[i + 1] - pathPoints[i], new Vector3(1f, 0f, 0f)) < 0)
                {
                    nextRot = -nextRot;
                }

                currentDist = (float)Math.Sqrt((double)((pathPoints[i].x - pathPoints[i - 1].x) * (pathPoints[i].x - pathPoints[i - 1].x)) +
                                                       ((pathPoints[i].z - pathPoints[i - 1].z) * (pathPoints[i].z - pathPoints[i - 1].z)));
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

            currentDist = (float)Math.Sqrt((double)((pathPoints[i].x - pathPoints[i - 1].x) * (pathPoints[i].x - pathPoints[i - 1].x)) +
                                                       ((pathPoints[i].z - pathPoints[i - 1].z) * (pathPoints[i].z - pathPoints[i - 1].z)));
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
            felice.transform.position = pathPoints[path.Count - 1];

            if (MySimpleNet != null)
            {
                MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = this.MovementIDExecuting, status = MsgActionExecutionStatus.Finished });
            }
        }

        this.CurrentMovementSpeed = 0;
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
		GameObject felice = GameObject.Find("felice_grasp");
        float degree = 0;
        float feliceAngle = (felice.transform.eulerAngles.y) % 360;
		
		if (Math.Abs(angle - feliceAngle) < 180)
		{
			degree = angle - feliceAngle;
		}
		else
		{
			if (angle > feliceAngle)
			{
				degree = (angle - feliceAngle) - 360;
			}
			else
			{
				degree = (angle - feliceAngle) + 360;
			}
		}

        this.IsCurrentMovementFinished = false;

        if (MySimpleNet != null)
        {
            MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = this.MovementIDExecuting, status = MsgActionExecutionStatus.Rotating });
        }

        // Rotation part

        Transform t = transform;
        float done = 0.0f;
        float total = Math.Abs(degree);
        float sgn = Math.Sign(degree);
        var startRot = t.eulerAngles;
        float maxSpeed = 50.0f;
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

        this.IsCurrentMovementFinished = true;

        // End of rotation part

        while (!this.IsCurrentMovementFinished)
        {
            yield return null;
        }

        this.IsCurrentMovementFinished = false;
        StartNewMovement(distance, angle);
        while (!this.IsCurrentMovementFinished)
        {
            yield return null;
        }

        goOn = true;
    }
}