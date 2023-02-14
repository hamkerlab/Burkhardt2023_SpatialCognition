/**
@brief Overloaded control class for the VR around several spatial cognition tasks

@details
 - Derived from BehaviourScript
 - Computes a grid map of the environment
 - Implements an A*-search for pathwalking
 - Intended to be used with the "SpatialCognition" scene

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

public class SpatialCognitionBehaviourScript : BehaviourScript
{	
	/// <summary>
	/// First part of the body displacement scenario completed?
	/// </summary>
	bool firstPartCompleted = false;
	
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
	
	/// <summary>
    /// All scene objects with Diffuse shader.
	/// </summary>
    GameObject sceneDiffuse;
    
	/// <summary>
    /// All scene objects with Nature/Tree Creator Leaves Fast shader.
	/// </summary>
    GameObject sceneTables;

    /// <summary>
    /// Helping member for bounding box modfication.
	/// </summary>
    float boundWidth = 10000.0f;

    /// <summary>
    /// Meshfilter of objects with Diffuse shader.
	/// </summary>
    Component[] mf1;
    
	/// <summary>
    /// Meshfilter of objects with Nature/Tree Creator Leaves Fast shader.
	/// </summary>
    Component[] mf2;

    /// <summary>
    /// World position of the objects on the table at the wall.
	/// </summary>
    Vector3[] tablePos;
    
	/// <summary>
    /// Index of the current object.
	/// </summary>
    int activeObj;
	
	//Main cameras
	public Camera MainCamera;
	public Camera MainCamera2;
	
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
			
    /// <summary>
    /// If spherical projection is enabled, the scene is cloned with a custom shader 
    /// and the original is hidden.
    /// Also: The color of the test objects is customly changed 
    /// due to color changes using custom shaders.
    /// </summary>
    protected override void Awake()
    {
        base.Awake();

        this.tablePos = new Vector3[5];

        this.tablePos[0] = GameObject.Find("racecar_green").transform.position;
        this.tablePos[1] = GameObject.Find("teddy").transform.position;
        this.tablePos[2] = GameObject.Find("carCraneYellow").transform.position;
        this.tablePos[3] = GameObject.Find("carCraneGreen").transform.position;
        this.tablePos[4] = GameObject.Find("pencil_blue_notEncoded").transform.position;
        activeObj = 3;
        sceneDiffuse = GameObject.Find("DiffuseShaders");
        sceneTables = GameObject.Find("NatureShaders");
		
		//The main cameras should render without the sperical shader:
		Shader rs = Shader.Find("Diffuse");
		MainCamera.SetReplacementShader(rs, "");	
		MainCamera2.SetReplacementShader(rs, "");
		
        if (this.config.sphericalProjection)
        {
			sceneDiffuse.SetActive(false);
            sceneDiffuse = Instantiate(sceneDiffuse) as GameObject;
            sceneDiffuse.SetActive(true);

            sceneTables.SetActive(false);
            sceneTables = Instantiate(sceneTables) as GameObject;
            sceneTables.SetActive(true);
            
            this.mf1 = this.sceneDiffuse.GetComponentsInChildren(typeof(MeshFilter));
            this.mf2 = this.sceneTables.GetComponentsInChildren(typeof(MeshFilter));

            Shader shader = Shader.Find("SphericalProjectionLit");
            Component[] smr = GameObject.Find("felice_grasp").GetComponentsInChildren(typeof(SkinnedMeshRenderer));
            float aspect = this.config.FovHorizontal / this.config.FovVertical;

            foreach (SkinnedMeshRenderer r in smr)
            {
                foreach (Material m in r.materials)
                {
                    m.shader = shader;
                    m.SetFloat("_FoVV", this.config.FovVertical);
                    m.SetFloat("_Aspect", aspect);
                    m.SetFloat("_F", Camera.main.farClipPlane);
                    m.SetFloat("_N", Camera.main.nearClipPlane);

                }
            }

            Component[] mr = sceneDiffuse.GetComponentsInChildren(typeof(MeshRenderer));

            foreach (MeshRenderer r in mr)
            {
                foreach (Material m in r.materials)
                {
                    m.shader = shader;
                    m.SetFloat("_FoVV", this.config.FovVertical);
                    m.SetFloat("_Aspect", aspect);
                    m.SetFloat("_F", Camera.main.farClipPlane);
                    m.SetFloat("_N", Camera.main.nearClipPlane);

                    // following could be better with switch
                    if (m.name == "wood_wall (Instance)")
                    {
                        m.SetColor("_Color", new Color(223.0f / 255.0f, 209.0f / 255.0f, 198.0f / 255.0f, 1));
                    }
                    if (m.name == "wood_wall2 (Instance)")
                    {
                        m.SetColor("_Color", new Color(252.0f / 255.0f, 230.0f / 255.0f, 209.0f / 255.0f, 1));
                    }
                    if (m.name == "car_crane_yellow (Instance)")
                    {
                        m.SetColor("_Color", new Color(235.0f / 255.0f, 232.0f / 255.0f, 43.0f / 255.0f, 1));
                    }
                    if (m.name == "car_crane_dark-gray (Instance)")
                    {
                        m.SetColor("_Color", new Color(124.0f / 255.0f, 124.0f / 255.0f, 124.0f / 255.0f, 1));
                    }
                    if (m.name == "car_crane_gray (Instance)")
                    {
                        m.SetColor("_Color", new Color(213.0f / 255.0f, 213.0f / 255.0f, 213.0f / 255.0f, 1));
                    }
                    if (m.name == "car_crane_chrome (Instance)")
                    {
                        m.SetColor("_Color", new Color(78.0f / 255.0f, 55.0f / 255.0f, 28.0f / 255.0f, 1));
                    }
					if (m.name == "car_crane_green (Instance)")
                    {
                        m.SetColor("_Color", new Color(0.0f / 255.0f, 211.0f / 255.0f, 5.0f / 255.0f, 1));
                    }
                    if (m.name == "pencil_blue (Instance)")
                    {
                        m.SetColor("_Color", new Color(157.0f / 255.0f, 176.0f / 255.0f, 244.0f / 255.0f, 1));
                    }
                    if (m.name == "pencil_yellow (Instance)")
                    {
                        m.SetColor("_Color", new Color(255.0f / 255.0f, 210.0f / 255.0f, 120.0f / 255.0f, 1));
                    }
                    if (m.name == "pencil_aqua (Instance)")
                    {
                        m.SetColor("_Color", new Color(172.0f / 255.0f, 235.0f / 255.0f, 247.0f / 255.0f, 1));
                    }
                    if (m.name == "pencil_gray (Instance)")
                    {
                        m.SetColor("_Color", new Color(118.0f / 255.0f, 118.0f / 255.0f, 118.0f / 255.0f, 1));
                    }
                    if (m.name == "racecar_gray (Instance)")
                    {
                        m.SetColor("_Color", new Color(132.0f / 255.0f, 132.0f / 255.0f, 132.0f / 255.0f, 1));
                    }
                    if (m.name == "racecar_green (Instance)")
                    {
                        m.SetColor("_Color", new Color(161.0f / 255.0f, 255.0f / 255.0f, 100.0f / 255.0f, 1));
                    }
                    if (m.name == "racecar_red (Instance)")
                    {
                        m.SetColor("_Color", new Color(218.0f / 255.0f, 0, 0, 1));
                    }
                    if (m.name == "racecar_white (Instance)")
                    {
                        m.SetColor("_Color", new Color(253.0f / 255.0f, 231.0f / 255.0f, 204.0f / 255.0f, 1));
                    }
                }
            }

            mr = sceneTables.GetComponentsInChildren(typeof(MeshRenderer));
            //shader = Shader.Find("TableWood");
            shader = Shader.Find("SphericalProjectionTableWood");
            foreach (MeshRenderer r in mr)
            {
                foreach (Material m in r.materials)
                {
                    m.shader = shader;
                    m.SetFloat("_FoVV", this.config.FovVertical);
                    m.SetFloat("_Aspect", aspect);
                    m.SetFloat("_F", Camera.main.farClipPlane);
                    m.SetFloat("_N", Camera.main.nearClipPlane);
                }
            }
        }	
    }
	
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	
	/// <summary>
    /// Overridden function for creation of the agent gameObject in the scene
    /// </summary>
    protected override void AgentInitalization()
    {
		// Find all agent OBJECTS  in the scene containing a specific script
		getAllAgentObjects<SpatialCognitionAgentScript>();
		
		// Find and init all agent SCRIPTS  in the scene containing a specific script
		getAndInitAllAgentScripts<SpatialCognitionAgentScript>();
		
		// Compute the grid map of the room
		computeGrid();
		
		// Create .txt files as output
		createTextfiles();
		
		//Initialize Felice position
		agentScripts[0].DefaultAgentPosition = new Vector3(9.0f,0.02f,6.0f);  //Felice position
		agentScripts[0].DefaultRotation = 180;
    }
	
	/// <summary>
    /// Overridden function for cloning the agent gameObject in the scene.
    /// Currently, only one agent supported.
    /// </summary>
    protected override void cloneAgent()
    {
        base.cloneAgent();
        if (this.config.sphericalProjection)
        {
            GameObject felice = GameObject.FindGameObjectWithTag("agent");
            GameObject clone = Instantiate(felice) as GameObject;
            clone.name = felice.name;                               // to get animations by name
            felice.name = "inactive Agent";                         // to be sure to be not considered in name search
            felice.SetActive(false);
        }
    }
	
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	
	/// <summary>
	/// Checks if given position is inside any bounding box (for computing the grid).
	/// </summary>
	/// <param name="x">x coordinate in world space</param>
	/// <param name="z">z coordinate in world space</param>
	/// <returns>int</returns>
	int checkPosition (int x, int z)
	{	
		foreach(GameObject go in allObjects) // allObjects is set in computeGrid()
		{
			if (go.activeInHierarchy && go.GetComponent<Collider>() && (go != agents[0]))
			{
				if(go.GetComponent<Collider>().bounds.Contains(gridPositions[x,z]))
				{
				   return 1;
				}
			}
		}	
		return 0;
	}
	
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
	
	/// <summary>
	/// Computes the grid map of the room.
	/// </summary>
	void computeGrid()
	{
		// Initialize
		for (int z = 0; z < gridResZ; z++)
		{
			for (int x = 0; x < gridResX; x++)
			{
				//gridPositions[x,z] = new Vector3(-(gridWidth/2) + ((gridWidth/gridResX)/2) + (x*(gridWidth/gridResX)), 1.0f, gridHeight - ((gridHeight/gridResZ)/2) - (z*(gridHeight/gridResZ)));
				gridPositions[x,z] = new Vector3(x, 1.0f, z);
				gridValue[x,z] = 0;
			}
		}
		allObjects = GameObject.FindSceneObjectsOfType(typeof(GameObject));
		
		// Check all grid positions for objects
		for (int z = 0; z < gridResZ; z++)
		{
			for (int x = 0; x < gridResX; x++)
			{
				if (checkPosition(x,z) != 0) // Object blocks this position
				{
					gridValue[x,z] = 1;
				}
				else
				{
					gridValue[x,z] = 0;
				}	
			}
		}	
		
		// Expand the objects a litte bit in their size (to prevent possible later collisions while moving the agent)
		for (int z = 0; z < gridResZ; z++)
		{
			for (int x = 0; x < gridResX; x++)
			{
				if (gridValue[x,z] == 0)
				{
					if (x == 0) // Left border
					{
						if (z == 0) // Upper left corner
						{
							if ((gridValue[x+1,z] == 1) || (gridValue[x,z+1] == 1) || (gridValue[x+1,z+1] == 1))
							{
								gridValue[x,z] = 2;
							}
						}
						else if (z == (gridResZ - 1)) // Lower left corner
						{
							if ((gridValue[x,z-1] == 1) || (gridValue[x+1,z-1] == 1) || (gridValue[x+1,z] == 1))
							{
								gridValue[x,z] = 2;
							}
						}
						else
						{
							if ((gridValue[x,z-1] == 1) || (gridValue[x+1,z-1] == 1) ||
								(gridValue[x+1,z] == 1) ||
								(gridValue[x,z+1] == 1) || (gridValue[x+1,z+1] == 1))
							{
								gridValue[x,z] = 2;
							}
						}
					}
					else if (x == (gridResX - 1)) // Right border
					{
						if (z == 0) // Upper right corner
						{
							if ((gridValue[x-1,z] == 1) || (gridValue[x-1,z+1] == 1) || (gridValue[x,z+1] == 1))
							{
								gridValue[x,z] = 2;
							}
						}
						else if (z == (gridResZ - 1)) // Lower right corner
						{
							if ((gridValue[x-1,z-1] == 1) || (gridValue[x,z-1] == 1) || (gridValue[x-1,z] == 1))
							{
								gridValue[x,z] = 2;
							}
						}
						else
						{
							if ((gridValue[x-1,z-1] == 1) || (gridValue[x,z-1] == 1) || 
							(gridValue[x-1,z] == 1) || 
							(gridValue[x-1,z+1] == 1) || (gridValue[x,z+1] == 1))
							{
								gridValue[x,z] = 2;
							}
						}	
					}
					else if (z == 0) // Upper border
					{
						if ((gridValue[x-1,z] == 1) || (gridValue[x+1,z] == 1) ||
							(gridValue[x-1,z+1] == 1) || (gridValue[x,z+1] == 1) || (gridValue[x+1,z+1] == 1))
						{
							gridValue[x,z] = 2;
						}
						
					}
					else if (z == (gridResZ - 1)) // Lower border
					{
						if ((gridValue[x-1,z-1] == 1) || (gridValue[x,z-1] == 1) || (gridValue[x+1,z-1] == 1) ||
							(gridValue[x-1,z] == 1) || (gridValue[x+1,z] == 1))
						{
							gridValue[x,z] = 2;
						}
					}
					else // No border
					{
						if ((gridValue[x-1,z-1] == 1) || (gridValue[x,z-1] == 1) || (gridValue[x+1,z-1] == 1) ||
							(gridValue[x-1,z] == 1) || (gridValue[x+1,z] == 1) ||
							(gridValue[x-1,z+1] == 1) || (gridValue[x,z+1] == 1) || (gridValue[x+1,z+1] == 1))
						{
							gridValue[x,z] = 2;
						}
					}
				}
			}
		}	
	}
	
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	
	/// <summary>
	/// Creates .txt files with informations about the scenarios.
	/// </summary>
	void createTextfiles()
	{
		// Write grid data in text file (blocked positions)
		System.IO.StreamWriter gridWriter = new System.IO.StreamWriter("ScenarioData/roomGrid.txt", false);			
		for (int z = 0; z < gridResZ+2; z++)
		{
			for (int x = 0; x < gridResX+2; x++)
			{
				if (x==gridResX+1) // Right wall
				{
					gridWriter.WriteLine(1);
				}
				else if (z==0 || x==0 || z==gridResZ+1) // Top, left or bottom wall
				{
					gridWriter.Write(1 + " ");
				}
				else // Inside the room
				{
					gridWriter.Write(gridValue[x-1,z-1] + " ");
				}	
			}		
		}
		gridWriter.Close();	
		
		// Write grid data in text file (different ID for every blocking object)
		System.IO.StreamWriter gridIDWriter = new System.IO.StreamWriter("ScenarioData/roomGridID.txt", false);	
		bool found = false; // true if one if the specia objects bocks the position
		for (int z = 0; z < gridResZ+2; z++)
		{
			for (int x = 0; x < gridResX+2; x++)
			{
				if (x==gridResX+1) // Right wall
				{
					gridIDWriter.WriteLine(1);
				}
				else if (z==0 || x==0 || z==gridResZ+1) // Top, left or bottom wall
				{
					gridIDWriter.Write(1 + " ");
				}
				else // Inside the room
				{
					if(gridValue[x-1,z-1] == 1)
					{
						foreach(GameObject go in allObjects) // allObjects is set in computeGrid()
						{
							if (go.activeInHierarchy && go.GetComponent<Collider>() && (go != agents[0]))
							{
								if(go.GetComponent<Collider>().bounds.Contains(gridPositions[x-1,z-1]))
								{
									if (go == GameObject.Find("table"))
									{
										gridIDWriter.Write(2 + " ");
										found = true;
									}
									else if (go == GameObject.Find("bed"))
									{
										gridIDWriter.Write(3 + " ");
										found = true;
									}
									else if (go == GameObject.Find("tableSmall"))
									{
										gridIDWriter.Write(4 + " ");
										found = true;
									}
									else if (go == GameObject.Find("Cube"))
									{
										gridIDWriter.Write(5 + " ");
										found = true;
									}
									else if (go == GameObject.Find("box"))
									{
										gridIDWriter.Write(6 + " ");
										found = true;
									}
									else if (go == GameObject.Find("shelf1"))
									{
										gridIDWriter.Write(7 + " ");
										found = true;
									}
									else if (go == GameObject.Find("shelf2"))
									{
										gridIDWriter.Write(8 + " ");
										found = true;
									}
									else if (go == GameObject.Find("sofa"))
									{
										gridIDWriter.Write(9 + " ");
										found = true;
									}
								}
							}
						}
						if (!found) // Position blocked but not from a special object
						{
							gridIDWriter.Write(1 + " ");
						}	
						found = false;
					}
					else // Position not blocked
					{
						gridIDWriter.Write(0 + " ");
					}

				}	
			}
		}
		gridIDWriter.Close();	
		
		// Write used objects, their IDs and positions in WS and the grid system in text file
		System.IO.StreamWriter objectPositionsWriter = new System.IO.StreamWriter("ScenarioData/roomGridPositions.txt", false);			
		objectPositionsWriter.Write(0 + "  ");
			objectPositionsWriter.Write("carCraneYellow  ");
			objectPositionsWriter.Write(getGridCoordinates(GameObject.Find("carCraneYellow").transform.position,false) + "  ");
			objectPositionsWriter.WriteLine(GameObject.Find("carCraneYellow").transform.position);
		objectPositionsWriter.Write(1 + "  ");
			objectPositionsWriter.Write("carCraneGreen  ");
			objectPositionsWriter.Write(getGridCoordinates(GameObject.Find("carCraneGreen").transform.position,false) + "  ");
			objectPositionsWriter.WriteLine(GameObject.Find("carCraneGreen").transform.position);
		objectPositionsWriter.Write(2 + "  ");
			objectPositionsWriter.Write("dog  ");
			objectPositionsWriter.Write(getGridCoordinates(GameObject.Find("dog").transform.position,false) + "  ");
			objectPositionsWriter.WriteLine(GameObject.Find("dog").transform.position);
		objectPositionsWriter.Write(3 + "  ");
			objectPositionsWriter.Write("carCrane  ");	
			objectPositionsWriter.Write(getGridCoordinates(GameObject.Find("carCrane").transform.position,false) + "  ");
			objectPositionsWriter.WriteLine(GameObject.Find("carCrane").transform.position);
		//objectPositionsWriter.Write(4 + "  ");
		//	objectPositionsWriter.Write("jellyRed  ");	
		//	objectPositionsWriter.Write(getGridCoordinates(GameObject.Find("jellyRed").transform.position,false) + "  ");
		//	objectPositionsWriter.WriteLine(GameObject.Find("jellyRed").transform.position);
		objectPositionsWriter.Write(5 + "  ");
			objectPositionsWriter.Write("penBlue  ");
			objectPositionsWriter.Write(getGridCoordinates(GameObject.Find("pencil_blue").transform.position,false) + "  ");
			objectPositionsWriter.WriteLine(GameObject.Find("pencil_blue").transform.position);
		objectPositionsWriter.Write(6 + "  ");
			objectPositionsWriter.Write("penGreen  ");
			objectPositionsWriter.Write(getGridCoordinates(GameObject.Find("pencil_green").transform.position,false) + "  ");
			objectPositionsWriter.WriteLine(GameObject.Find("pencil_green").transform.position);
		//objectPositionsWriter.Write(7 + "  ");
		//	objectPositionsWriter.Write("penBlack  ");
		//	objectPositionsWriter.Write(getGridCoordinates(GameObject.Find("pencil_black").transform.position,false) + "  ");
		//	objectPositionsWriter.WriteLine(GameObject.Find("pencil_black").transform.position);
		objectPositionsWriter.Write(8 + "  ");
			objectPositionsWriter.Write("penRed  ");
			objectPositionsWriter.Write(getGridCoordinates(GameObject.Find("pencil_red").transform.position,false) + "  ");
			objectPositionsWriter.WriteLine(GameObject.Find("pencil_red").transform.position);
		objectPositionsWriter.Close();	
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
	
	/// <summary>
	/// Starts setup.
	/// </summary>
	/// <param name="msg">protobuf message</param>
	protected override void ProcessMsgEnvironmentReset( MsgEnvironmentReset msg )
    {			
		switch(msg.Type)
		{
		// Object recognition
		case 0:
			agentScripts[0].DefaultAgentPosition = new Vector3(-4.6f,0.02f,13.0f); 
			agentScripts[0].DefaultRotation = 180;
			GameObject.Find("MainCamera").transform.position = new Vector3(-3.59f,4.82f,12.61f); 
			GameObject.Find("MainCamera").transform.eulerAngles = new Vector3(58.0f,-98.0f,358.5f); 
			break;
		// Body displacement
		case 1:
			agentScripts[0].DefaultAgentPosition = new Vector3(-0.1f,0.02f,3.5f); 
			agentScripts[0].DefaultRotation = 180;
			GameObject.Find("MainCamera").transform.position = new Vector3(0.51f,5.0f,3.9f); 
			GameObject.Find("MainCamera").transform.eulerAngles = new Vector3(62.5f,251.0f,358.5f);
			break;
		// Memory learning
		case 2:
			agentScripts[0].DefaultAgentPosition = new Vector3(1.4f,0.02f,3.3f); 
			agentScripts[0].DefaultRotation = 180;
			GameObject.Find("MainCamera").transform.position = new Vector3(-4.93f,11.26f,6.38f); 
			GameObject.Find("MainCamera").transform.eulerAngles = new Vector3(52.0f,69.3f,358.5f);		
			break;
		// Vision and memory
		case 3:
			agentScripts[0].DefaultAgentPosition = new Vector3(8.0f,0.02f,17.0f); 
			agentScripts[0].DefaultRotation = 180; //135 with center table
			GameObject.Find("MainCamera").transform.position = new Vector3(5f,11.26f,6.38f); 
			GameObject.Find("MainCamera").transform.eulerAngles = new Vector3(52.0f,69.3f,358.5f);
			GameObject.Find("MainCamera2").transform.position = new Vector3(10.0f,15.0f,10.0f); 
			GameObject.Find("MainCamera2").transform.eulerAngles = new Vector3(90.0f,0.0f,0.0f);
			break;
		// Multiple attention pointers
		case 4:
			agentScripts[0].DefaultAgentPosition = new Vector3(0.45f,0.02f,7.5f); 
			agentScripts[0].DefaultRotation = 0;
			GameObject.Find("MainCamera").transform.position = new Vector3(-0.92f,4.09f,8.23f); 
			GameObject.Find("MainCamera").transform.eulerAngles = new Vector3(52.0f,114.03f,358.5f); 
			//GameObject.Find("pencil_red").transform.position = new Vector3(0.241f,1.89f,8.48f); 
			break;
		default:
			agentScripts[0].DefaultAgentPosition = new Vector3(0f,0f,10f);
			break;
		}		
		
		Reset();
    }
	
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	
	/// <summary>
	/// Used to schedule some environmental things with a message from agent side.
	/// </summary>
	protected override void ProcessMsgTrialReset( MsgTrialReset msg )
    {			
		switch(msg.Type)
		{
			
		// Body displacement
		case 0:
			if (!firstPartCompleted)
			{
				StartCoroutine(FirstPart());
				firstPartCompleted = true;
			}
			else
			{
				StartCoroutine(SecondPart());
				firstPartCompleted = false;
			}
			break;
			
		// Multiple attention pointers
		case 1:
			GameObject.Find("penRed").transform.position = new Vector3(0.241f,-10.0f,8.48f); 
			break;
			
		default:
			break;
		}		
    }
	
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	
	/// <summary>
	/// Coroutine for flashing target and moving agent (body displacement scenario)
	/// </summary>
	IEnumerator FirstPart()
	{
		float remaining = 1.4f;
		
		// Target flashing
		GameObject.Find("carCrane").transform.position = new Vector3(0.1f,-10.0f,1.8f); 
		yield return new WaitForSeconds(1.0f);
		GameObject.Find("carCrane").transform.position = new Vector3(0.1f,2.08f,1.8f); 
		yield return new WaitForSeconds(1.0f);
		GameObject.Find("carCrane").transform.position = new Vector3(0.1f,-10.0f,1.8f); 
		yield return new WaitForSeconds(1.0f);
		
		// Agent side movement
		while (remaining > 0.0f)
		{ 
			float translation = 1.0f * Time.deltaTime;
			agentScripts[0].transform.Translate(translation,0.0f, 0.0f);
			remaining -= translation;
			yield return null;
		}
	}
	
	/// <summary>
	/// Coroutine for revealing the target (end of body displacement scenario)
	/// </summary>
	IEnumerator SecondPart()
	{
		yield return new WaitForSeconds(1.0f);
		GameObject.Find("carCrane").transform.position = new Vector3(0.1f,2.08f,1.8f); 
		yield return new WaitForSeconds(2.0f);
		GameObject.Find("carCrane").transform.position = new Vector3(0.1f,-10.0f,1.8f); 	
	}	
}