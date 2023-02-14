/**
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using SimpleNetwork;

using UnityEngine;


public class TestObjectBehaviourScript : BehaviourScript {

	// Spawn point enumeration
	public enum level 
	{
		spawn1 = 1,
		spawn2 = 2
	};

	// Selected spawn point
	public level select = level.spawn1;


	GameObject agent;


/// <summary>
	/// Width of the grind
	/// </summary>
	static float gridWidth = 20.0f;
	/// <summary>
	/// Height of the grind
	/// </summary>
	static float gridHeight = 20.0f;
	
	/// <summary>
	/// Grid resolution in X direction
	/// </summary>
	static int gridResX = 20;
	/// <summary>
	/// Grid resolution in Z direction
	/// </summary>
	static int gridResZ = 20;
	
	/// <summary>
	/// World space positions of the grid nodes
	/// </summary>
	public Vector3[,] gridPositions = new Vector3[gridResX,gridResZ]; // public for use in SpatialCognitionAgentScript
	
	/// <summary>
	/// 0 = empty, 1 = blocked, 2 = empty space around object-borders
	/// </summary>
	int[,] gridValue = new int[gridResX,gridResZ];
	
	/// <summary>
	/// All game objects (needed for computing the grid)
	/// </summary>
	object[] allObjects;



	// Initalization
	protected override void AgentInitalization()
	{		
		// find all agent OBJECTS  in the scene containing a specific script
		getAllAgentObjects<TestObjectAgentScript>();
		
		// find and init all agent SCRIPTS  in the scene containing a specific script
		getAndInitAllAgentScripts<TestObjectAgentScript>();

		// set default position to selected spawn point
		switch((int)select){
			case 1:
				agentScripts[0].DefaultAgentPosition = new Vector3(2.07f,0.25f,-6.35f); 
				break;
			case 2:
				agentScripts[0].DefaultAgentPosition = new Vector3(2f,0.25f,-16.5975f);
				break;
		}

		agentScripts[0].DefaultRotation = 0;

		Reset();
		
	}

	// Reset environment
	protected override void ProcessMsgEnvironmentReset( MsgEnvironmentReset msg )
	{			
 		
		Reset();
	}
	

	////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	
	/// <summary>
	/// A* search
	/// </summary>
	/// <param name="start">Start point of the path in world space</param>
	/// <param name="target">Destination point of the path in world space</param>
	/// <returns>List<int></returns>
	public List<int> computePath(Vector3 start, Vector3 target)
	{
		int gridRes = gridResX * gridResZ; // grid resolution
		int[] H = new int[gridRes]; // Heuristic
		int[] G = new int[gridRes]; // Movement cost
		int[] F = new int[gridRes]; // G + H
		int[] P = new int[gridRes]; // Parent
		List<int> open = new List<int>(); // Nodes to process
		List<int> closed = new List<int>(); // Nodes already done
		int startNumber = 0, targetNumber = 0; // Numbers of start and target points in the grid
		bool pathFound = false;
		int current; // Current node
		
		// Map start and target point to the grid
		Vector2 gridStart = getGridCoordinates(start, true);
		Vector2 gridTarget = getGridCoordinates(target, true);
		
		// Numbers of start and target positions in the grid
		startNumber = (int)gridStart.x + ((int)gridStart.y * gridResX); 
		targetNumber = (int)gridTarget.x + ((int)gridTarget.y * gridResX);
		
		// Compute H (manhattan distance to target) and initialize G and F
		for (int z = 0; z < gridResZ; z++)
		{
			for (int x = 0; x < gridResX; x++)
			{
				if (gridValue[x,z] == 0)
				{
					H[x + (z*gridResX)] = Math.Abs((int)gridTarget.x -x) + Math.Abs((int)gridTarget.y - z);
					G[x + (z*gridResX)] = 0; 
					F[x + (z*gridResX)] = 0; 
				}
			}
		}
		
		open.Add(startNumber);
		current = startNumber;
		
		while (!pathFound)
		{
			// Choose next point
			current = open[0];
			for (int i = 1; i < open.Count; i++)
			{
				if (F[open[i]] < F[current])
				{
					current = open[i];
				}
			}
			open.Remove(current);
			closed.Add(current);

			int[] neighbours = new int[8]; // Neighbours of the current node
			
			// Set neighbours (999 means blocked or outside the grid)
			if (current < gridResX) // Upper border
			{
				if (current == 0) // Upper left corner
				{
					neighbours[0] = 999; // Upper
					neighbours[1] = current + gridResX; // Bottom
					neighbours[2] = 999;  // Left
					neighbours[3] = current + 1;  // Right
					neighbours[4] = 999; // Upper left
					neighbours[5] = 999; // Upper right
					neighbours[6] = 999; // Bottom left
					neighbours[7] = current + (gridResX + 1); // Bottom right
				}
				else if (current == (gridResX -1)) // Upper right corner
				{
					neighbours[0] = 999; // Upper
					neighbours[1] = current + gridResX; // Bottom
					neighbours[2] = current - 1;  // Left
					neighbours[3] = 999;  // Right
					neighbours[4] = 999; // Upper left
					neighbours[5] = 999; // Upper right
					neighbours[6] = current + (gridResX - 1); // Bottom left
					neighbours[7] = 999; // Bottom right
				}
				else
				{
					neighbours[0] = 999; // Upper
					neighbours[1] = current + gridResX; // Bottom
					neighbours[2] = current - 1;  // Left
					neighbours[3] = current + 1;  // Right
					neighbours[4] = 999; // Upper left
					neighbours[5] = 999; // Upper right
					neighbours[6] = current + (gridResX - 1); // Bottom left
					neighbours[7] = current + (gridResX + 1); // Bottom right
				}	
			}
			else if (current > (gridRes - gridResX -1)) // Lower border
			{
				if (current == (gridRes - gridResX)) // Lower left corner
				{
					neighbours[0] = current - gridResX; // Upper
					neighbours[1] = 999; // Bottom
					neighbours[2] = 999;  // Left
					neighbours[3] = current + 1;  // Tight
					neighbours[4] = 999; // Upper left
					neighbours[5] = current - (gridResX - 1); // Upper right
					neighbours[6] = 999; // Bottom left
					neighbours[7] = 999; // Bottom right
				}
				else if (current == (gridRes -1)) // Lower right corner
				{
					neighbours[0] = current - gridResX; // Upper
					neighbours[1] = 999; // Bottom
					neighbours[2] = current - 1;  // Left
					neighbours[3] = 999;  // Right
					neighbours[4] = current - (gridResX + 1); // Upper left
					neighbours[5] = 999; // Upper right
					neighbours[6] = 999; // Bottom left
					neighbours[7] = 999; // Bottom right
				}
				else 
				{
					neighbours[0] = current - gridResX; // Upper
					neighbours[1] = 999; // Bottom
					neighbours[2] = current - 1;  // Left
					neighbours[3] = current + 1;  // Right
					neighbours[4] = current - (gridResX + 1); // Uupper left
					neighbours[5] = current - (gridResX - 1); // Upper right
					neighbours[6] = 999; // Bottom left
					neighbours[7] = 999; // Bottom right
				}	
			}
			else if (current % gridResX == 0) // Left border
			{
				neighbours[0] = current - gridResX; // Upper
				neighbours[1] = current + gridResX; // Bottom
				neighbours[2] = 999;  // Left
				neighbours[3] = current + 1;  // Right
				neighbours[4] = 999; // Upper left
				neighbours[5] = current - (gridResX - 1); // Upper right
				neighbours[6] = 999; // Bottom left
				neighbours[7] = current + (gridResX + 1); // Bottom right
			}
			else if (current % (gridResX - 1) == 0) // Right border
			{
				neighbours[0] = current - gridResX; // Upper
				neighbours[1] = current + gridResX; // Bottom
				neighbours[2] = current - 1;  // Left
				neighbours[3] = 999;  // Right
				neighbours[4] = current - (gridResX + 1); // Upper left
				neighbours[5] = 999; // Upper right
				neighbours[6] = current + (gridResX - 1); // Bottom left
				neighbours[7] = 999; // Bottom right
			}
			else // No border point
			{
				neighbours[0] = current - gridResX; // Upper
				neighbours[1] = current + gridResX; // Bottom
				neighbours[2] = current - 1;  // Left
				neighbours[3] = current + 1;  // Right
				neighbours[4] = current - (gridResX + 1); // Upper left
				neighbours[5] = current - (gridResX - 1); // Upper right
				neighbours[6] = current + (gridResX - 1); // Bottom left
				neighbours[7] = current + (gridResX + 1); // Bottom right
			}
			
			for (int i = 0; i < 8; i++)
			{
				if (neighbours[i] != 999)
				{
					if (gridValue[(neighbours[i] % gridResX),(neighbours[i] / gridResX)] != 0) // Point blocked
					{
						neighbours[i] = 999;
					}
				}
			}
		
			// Compute values of P, G and F (see above) for all neighbours of the current checked grid node
			for (int i = 0; i < 8; i++)
			{
				if (neighbours[i] == targetNumber)
				{
					P[targetNumber] = neighbours[i];
					pathFound = true;
				}
				if (!closed.Contains(neighbours[i])  // Point not in closed list
					&& neighbours[i] != 999)		 // Point not blocked or outside the grid
				{
					if (open.Contains(neighbours[i])) // Point in open list
					{
						// Set G value
						if (i > 3) // Straight way
						{
							if (G[neighbours[i]] > (G[current] + 10))
							{
								// Set parent 
								P[neighbours[i]] = current;
								
								// Set G
								G[neighbours[i]] = (G[current] + 10);
								
								// Compute F
								F[neighbours[i]] = H[neighbours[i]] + G[neighbours[i]];
							}
						}
						else // Diagonal way
						{
							if (G[neighbours[i]] > (G[current] + 14))
							{
								// Set parent 
								P[neighbours[i]] = current;
								
								// Set G
								G[neighbours[i]] = (G[current] + 14);
								
								// Compute F
								F[neighbours[i]] = H[neighbours[i]] + G[neighbours[i]];
							}
						}
					}
					else
					{
						// Add neighbour of current point to the open list
						open.Add (neighbours[i]);
						
						// Set G value
						if (i < 4) // Straight way
						{
							G[neighbours[i]] = 10 + G[current];
						}
						else // Diagonal way
						{
							G[neighbours[i]] = 14 + G[current];
						}
						
						// Compute F
						F[neighbours[i]] = H[neighbours[i]] + G[neighbours[i]];
						
						// Set parent 
						P[neighbours[i]] = current;
					}
				}				
			}

            if (!pathFound && (open.Count == 0)) // No more point available to reach the target
            {
                Debug.Log("No path available!");
                return null;
            }
		}
		
		// Trace back the path
		bool pathComplete = false;
		List<int> path = new List<int>();
		int nextPoint = targetNumber;
		path.Add(targetNumber);
		while (!pathComplete)
		{
			nextPoint = P[nextPoint];
			path.Add(nextPoint);
			if (nextPoint == startNumber)
			{
				pathComplete = true;
			}
		}
		path.Reverse();
		return path;
	}
	
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////	


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	
	/// <summary>
	/// Maps a given world space position on the nearest grid coordinates.
	/// </summary>
	/// <param name="positionWS">position in world space</param>
	/// <param name="free">if true, position has to be free</param>
	/// <returns>Vector2</returns>
	Vector2 getGridCoordinates(Vector3 positionWS, bool free)
	{
		float smallest = 999.0f, current = 999.0f; // Distance variables for finding the smallest distance
		float gridX = 0f, gridZ = 0f;
		
		if (free)
		{
			for (int z = 0; z < gridResZ; z++)
			{
				for (int x = 0; x < gridResX; x++)
				{
					if (gridValue[x,z] == 0)
					{
						current =  Convert.ToInt32(Math.Sqrt(  (double)(((positionWS.x - gridPositions[x,z].x) * (positionWS.x - gridPositions[x,z].x)) +
																		((positionWS.y - gridPositions[x,z].y) * (positionWS.y - gridPositions[x,z].y)) +
																		((positionWS.z - gridPositions[x,z].z) * (positionWS.z - gridPositions[x,z].z))) ));
	
						if (current < smallest) 
						{
							smallest = current;
							gridX = x;
							gridZ = z;
						}
					}
				}
			}
		}
		else 
		{
			for (int z = 0; z < gridResZ; z++)
			{
				for (int x = 0; x < gridResX; x++)
				{
					current =  Convert.ToInt32(Math.Sqrt(  (double)(((positionWS.x - gridPositions[x,z].x) * (positionWS.x - gridPositions[x,z].x)) +
																	((positionWS.y - gridPositions[x,z].y) * (positionWS.y - gridPositions[x,z].y)) +
																	((positionWS.z - gridPositions[x,z].z) * (positionWS.z - gridPositions[x,z].z))) ));

					if (current < smallest) 
					{
						smallest = current;
						gridX = x;
						gridZ = z;
					}
				}
			}
		}
		
		Vector2 result = new Vector2(gridX,gridZ);
		return result;
	}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

}
