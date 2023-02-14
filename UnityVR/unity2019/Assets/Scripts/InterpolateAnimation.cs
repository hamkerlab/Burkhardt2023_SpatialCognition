/**
@brief Class for interpolating/blending 3 grasp-animations to grasp an intermediate position. This class is finding the smallest triangle to blend animation. 
 
@details
 - Idea: 
   - Class stores a list of existing animations and their final coordinates
   - it constructs from this point list an list of triangles
   - It then receives an target point to grasp and find the smallest triangle containing this point (see animate(...) )
   - Then it calculates euklidean distance from the target to the trianlge vertex (corner points)
   - These values are used as factors to blend 3 animations together
 
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using UnityEngine;
using System.Collections;
using System;
using SimpleNetwork;
using System.Globalization;
using System.IO;

public class InterpolateAnimations
{
	/// store all point in a list of empty game objects (we could also use Vector3, but we were lazy...)
	GameObject[] gObjects;
	 
    /// array stores animations for blending
    public string[] animationArray {get;private set;}	
  
    /// weight of blending current animation
    float s, t, u;

	/// objects at the corner of the triangle, to define the corners
	GameObject A = new GameObject();
	GameObject B = new GameObject();
    GameObject C = new GameObject(); 
   
	/// Associated agent
	AgentScript Agent; 
	
	/// <summary>
	/// Storing one triangle.
	/// </summary>
	public struct Triangle
	{
		public int vertex1;
		public int vertex2;
		public int vertex3;
	}
	
	//array contain points of all triangles
    Triangle[] triangle ;
	
	//We finally assign vertex of smallest triangle to this structre
    Triangle minTriangle = new Triangle();		
	
	
	
	#region Public functions
		
	/// <summary>
	/// Initializes a new instance of the <see cref="InterpolateAnimations"/> class.
	/// </summary>
	/// <param name='Agent'>
	/// Associated agent.
	/// </param>
	/// <param name='animationCoordFile'>
	/// Target coordinates of all animations should be stored in this cvs-file.
	/// </param>
	/// <param name='animationArray'>
	/// List of all animation names.
	/// </param>	
	public InterpolateAnimations(AgentScript Agent, string animationCoordFile)
	{
		this.Agent = Agent;
		
		//load animationCoodrinates from file and set gameobjects coordinates
		ReadCSV(animationCoordFile);
		
		// high enough number to store all triangles (maximum possible combinations) => 560 for 16 animations
		triangle = new Triangle[BinC(animationArray.Length, 3)];		
		
		//create all triangles from this
		FindTriangle(); // find triangles and sort cornerpoints of each triangle
		
	}
	
	/// <summary>
	/// Executes an animation towards the target point (targetX, targetY, targetZ).
	/// </summary>
	/// <param name='targetX'>
	/// Target x-coordinate.
	/// </param>
	/// <param name='targetY'>
	/// Target y-coordinate.
	/// </param>
	/// <param name='targetZ'>
	/// Target z-coordinate.
	/// </param>
	/// <returns>
	/// True if target is in the range of the animations, hence if it is inside at least one triangle spaned by the animation target points.
	/// </returns>   
  	public bool animate(float targetX, float targetY, float targetZ)
	{
		 //determines blending parameter and store them in s,t,u
		 // returns false if this is not possible, hence grasping is not possible
		 if(CalculateAnimateWeights(targetX, targetY, targetZ))
		{
		      //For blending animation
	         Agent.GetComponent<Animation>().Blend(animationArray[minTriangle.vertex1], s);
	         Agent.GetComponent<Animation>().Blend(animationArray[minTriangle.vertex2], t);
	         Agent.GetComponent<Animation>().Blend(animationArray[minTriangle.vertex3], u);
			 return true;
		}
		else
		{
			return false;
		}
	
	}
	
	#endregion
	
	#region Internal function determine 3 minimum triangle and interpolations weights
 
    
    /// <summary>
	/// Calculate the weights to blend 3 animations together.
    /// - Do it by finding first the minimum triangle.
	///   - Find smallest triangle containing the target (x,y,z). Use currently only X and Z and assume the target is on the table
	///   - Uses stupid brute-force
	/// - If the min triangle is found, calculate weights from euklidean distance
	/// </summary>
	/// <returns>
	/// True if target is in the range of the animations, hence if it is inside at least one triangle spaned by the animation target points.
	/// </returns>   
    bool CalculateAnimateWeights (float targetX, float targetY, float targetZ)
    {
        float minCircle = 0; //currently founded minimum triangle (circle = a+b+c)
		bool found = false; //true if the target is at least inside one triangle
		
		for (int i = 0; i < triangle.Length; i++) 
		{        
			
            //Assignt A,B,C //A,B,C is global variables
            DetermineTriangleCorners(i);

            //To control so that target is inside (or outside )
			if (CheckInsideAndCalcWeight(A.transform.position.x,A.transform.position.z,
                B.transform.position.x,B.transform.position.z,
                C.transform.position.x,C.transform.position.z,
                targetX, targetZ))
            {
				found = true;

                //distance between A-B
                float x = (Mathf.Pow(Mathf.Abs (gObjects[triangle[i].vertex1].transform.position.x -
                           gObjects[triangle[i].vertex2].transform.position.x),2) + 
                           Mathf.Pow(Mathf.Abs(gObjects[triangle[i].vertex1].transform.position.z - 
                           gObjects[triangle[i].vertex2].transform.position.z),2));

                //distance between A-C
                float y = Mathf.Pow(Mathf.Abs (gObjects[triangle[i].vertex1].transform.position.x -
                           gObjects[triangle[i].vertex3].transform.position.x),2) + 
                           Mathf.Pow(Mathf.Abs(gObjects[triangle[i].vertex1].transform.position.z - 
                           gObjects[triangle[i].vertex3].transform.position.z),2);

                // distance between B-C
                float z = Mathf.Pow(Mathf.Abs (gObjects[triangle[i].vertex2].transform.position.x -
                           gObjects[triangle[i].vertex3].transform.position.x),2) + 
                           Mathf.Pow(Mathf.Abs(gObjects[triangle[i].vertex2].transform.position.z - 
                           gObjects[triangle[i].vertex3].transform.position.z),2);

                //root of x,y,z because of hipotenus
                x = Mathf.Sqrt(x); // |A-B|
                y = Mathf.Sqrt(y);//  |A-C|
                z = Mathf.Sqrt(z);//  |B-C|

                //find minimum sum of the sides (min (a+b+c))
                //circleMin is the minimum of (a+b+c)

                //check if minCircle=0 , assign first value to minCircle
                if (minCircle == 0)
                {
                    minCircle = x + y + z;
                    minTriangle.vertex1 = triangle[i].vertex1;
                    minTriangle.vertex2 = triangle[i].vertex2;
                    minTriangle.vertex3 = triangle[i].vertex3;                    
                }

                //if minCircle is not 0, compare values for finding smallest triangle with smallest circle
                else
                {
                    if (x == 0 && y == 0 && z == 0)
                    {
                        //nothing
                    }
                    else
                    {
                        if (minCircle > (x + y + z))
                        {
                            minCircle = x + y + z;
                            minTriangle.vertex1 = triangle[i].vertex1;
                            minTriangle.vertex2 = triangle[i].vertex2;
                            minTriangle.vertex3 = triangle[i].vertex3;
                        }
                    }
                }
            }           
		}
		if(!found)
			return false;
		
		//Debug.Log("Min circle: = " +  minCircle); //TODEL
		
		//DEBUG: print which points is creating triangle
		/*Debug.Log("A: "+gObjects[minTriangle.vertex1].transform.name + "    B: " + 
                         gObjects[minTriangle.vertex2].transform.name + "    C: " +
                         gObjects[minTriangle.vertex3].transform.name);*/
		
        // Assign to s,t and u value returning from controlInside function.
		// - Have to be done again as he current s,t,u can belong to a not-minal triangle containing the target.
        return CheckInsideAndCalcWeight(gObjects[minTriangle.vertex1].transform.position.x,gObjects[minTriangle.vertex1].transform.position.z, 
             gObjects[minTriangle.vertex2].transform.position.x, gObjects[minTriangle.vertex2].transform.position.z,
             gObjects[minTriangle.vertex3].transform.position.x, gObjects[minTriangle.vertex3].transform.position.z, 
             targetX, targetZ);
         
    }
	
	 /// <summary>
	/// Figure out which point belong to each corner (A,B,C) of a given triangle
	/// </summary>
	/// <param name='a'>
	/// Triangle index
	/// </param>
    void DetermineTriangleCorners(int a)
	{
		int vertex = 0;
		
		//trying to find A
		//Point having smallest y axis is A
		if (gObjects[triangle[a].vertex1].transform.position.z < gObjects[triangle[a].vertex2].transform.position.z) 
        {
			if (gObjects[triangle[a].vertex1].transform.position.z < gObjects[triangle[a].vertex3].transform.position.z) 
            {
				A = gObjects[triangle[a].vertex1];
				vertex = 1;
			}
			else {
				A = gObjects[triangle[a].vertex3];
				vertex = 3;
			}
		}
		else if (gObjects[triangle[a].vertex2].transform.position.z < gObjects[triangle[a].vertex3].transform.position.z) 
        {
			A = gObjects[triangle[a].vertex2];
			vertex = 2;
		}
		else if (gObjects[triangle[a].vertex2].transform.position.z > gObjects[triangle[a].vertex3].transform.position.z) 
        {
			A = gObjects[triangle[a].vertex3];
            vertex = 3;
		}

        //trying to find B and C point of triangle
		//Point have smallest slope between  A and own is B. Other is C.
        switch (vertex)
        {
			//if vertex1 is A
            case 1:

                //slope s1 and s2
                double s1 = (double) (gObjects[triangle[a].vertex2].transform.position.z-A.transform.position.z) /
                    (gObjects[triangle[a].vertex2].transform.position.x - A.transform.position.x );
                double s2 = (double) (gObjects[triangle[a].vertex3].transform.position.z-A.transform.position.z) /
                    (gObjects[triangle[a].vertex3].transform.position.x - A.transform.position.x );
			
				
                if(s1 < 0)
                {

                   
					//if s1<0 and s2>=0 then
                    if(s2 >= 0)
                    {
                        B = gObjects[triangle[a].vertex3];
                        C = gObjects[triangle[a].vertex2];
                    }
					//if s1<0 and s2<0 then
                    else
	                {
					
						//s1, s2<0 and |s1| < |s2| 
                        if( System.Math.Abs(s1) < System.Math.Abs(s2))
                        {
                            B = gObjects[triangle[a].vertex3];
                            C = gObjects[triangle[a].vertex2];
                        }
					
						//s1,s2<0 and |s1| > |s2|
                        else if(Math.Abs(s1) > Math.Abs(s2))
                        {
                            B = gObjects[triangle[a].vertex2];
                            C = gObjects[triangle[a].vertex3];
                        }
                    }
                }
                else if (s1 > 0)
                {
                   
                    if (s2 > 0)
                    {
                        if (s1 > s2)
                        {
                            C = gObjects[triangle[a].vertex2];
                            B = gObjects[triangle[a].vertex3];
                        }
                        else if (s1 < s2)
                        {
                            C = gObjects[triangle[a].vertex3];
                            B = gObjects[triangle[a].vertex2];
                        }
                    }
                    else if (s2 < 0)
                    {
                        B = gObjects[triangle[a].vertex2];
                        C = gObjects[triangle[a].vertex3];
                    }

                }break;
			
				//if vertex2 is A
                case 2:

                //slope s1 and s2
                double s3 = (double) (gObjects[triangle[a].vertex1].transform.position.z-A.transform.position.z) /
                    (gObjects[triangle[a].vertex1].transform.position.x - A.transform.position.x );
                double s4 = (double) (gObjects[triangle[a].vertex3].transform.position.z-A.transform.position.z) /
                    (gObjects[triangle[a].vertex3].transform.position.x - A.transform.position.x );

                if(s3 < 0)
                {
                    if(s4 >= 0)
                    {
                        B = gObjects[triangle[a].vertex3];
                        C = gObjects[triangle[a].vertex1];
                    }
                    else
	                {
                        if( System.Math.Abs(s3) < System.Math.Abs(s4))
                        {
                            B = gObjects[triangle[a].vertex3];
                            C = gObjects[triangle[a].vertex1];
                        }
                        else if(Math.Abs(s3) > Math.Abs(s4))
                        {
                            B = gObjects[triangle[a].vertex1];
                            C = gObjects[triangle[a].vertex3];
                        }
                    }
                }
                else if (s3 > 0)
                {
                    if (s4 > 0)
                    {
                        if (s3 > s4)
                        {
                            C = gObjects[triangle[a].vertex1];
                            B = gObjects[triangle[a].vertex3];
                        }
                        else if (s3 < s4)
                        {
                            B = gObjects[triangle[a].vertex3];
                            C = gObjects[triangle[a].vertex1];
                        }
                    }
                    else if (s4 < 0)
                    {
                        B = gObjects[triangle[a].vertex1];
                        C = gObjects[triangle[a].vertex3];
                    }

                }break;

			
				//if vertex3 is A
                case 3:

                //slope s1 and s2
                double s5 = (double) (gObjects[triangle[a].vertex2].transform.position.z-A.transform.position.z) /
                    (gObjects[triangle[a].vertex2].transform.position.x - A.transform.position.x );
                double s6 = (double) (gObjects[triangle[a].vertex1].transform.position.z-A.transform.position.z) /
                    (gObjects[triangle[a].vertex1].transform.position.x - A.transform.position.x );

                if(s5 < 0)
                {
                    if(s6 >= 0)
                    {
                        B = gObjects[triangle[a].vertex1];
                        C = gObjects[triangle[a].vertex2];
                    }
                    else
	                {
                        if( System.Math.Abs(s5) < System.Math.Abs(s6))
                        {
                            B = gObjects[triangle[a].vertex1];
                            C = gObjects[triangle[a].vertex2];
                        }
                        else if(Math.Abs(s5) > Math.Abs(s6))
                        {
                            B = gObjects[triangle[a].vertex2];
                            C = gObjects[triangle[a].vertex1];
                        }
                    }
                }
                else if (s5 > 0)
                {
                    if (s6 > 0)
                    {
                        if (s5 > s6)
                        {
                            C = gObjects[triangle[a].vertex2];
                            B = gObjects[triangle[a].vertex1];
                        }
                        else if (s5 < s6)
                        {
                            C = gObjects[triangle[a].vertex1];
                            B = gObjects[triangle[a].vertex2];
                        }
                    }
                    else if (s6 < 0)
                    {
                        B = gObjects[triangle[a].vertex2];//
                        C = gObjects[triangle[a].vertex1];
                    }

                }break;
        }
		
		//order inside of structre so that vertex1=A,vertex2=B, vertex3=C
		triangle[a].vertex1 = Array.IndexOf(gObjects,A);
		triangle[a].vertex2 = Array.IndexOf(gObjects,B);
		triangle[a].vertex3 = Array.IndexOf(gObjects,C);

    }
	
	/// <summary>
	/// Check whether a point P is inside or outside a trianlge A,B,C and calculate eukledian distances if inside.
    /// There are 4 point.ax,ay = 1st point, bx,by = 2nd point, cx,cy = 3rd point, px,py = 4th point
    /// the last point is P point so we have to control this point whether is located in triangle
	/// </summary>
	/// <returns>
	/// True if inside, false if outside.
	/// </returns>
    bool CheckInsideAndCalcWeight(float ax, float ay, float bx, float bY, float cx, float cy, float px, float py)
    {	
		//det(A)
        float det = (ax * bY + ay * cx + bx * cy) - (bY * cx + ax * cy + ay * bx);
        if (det <= 0)
        {
			//point is outside
			s = 0; t = 0; u = 0;
            return false;
        }
        else
        {
            // animation rate
            s = (1 / det) * ((bY - cy) * px + (cx - bx) * py + (bx * cy - cx * bY));
            t = (1 / det) * ((cy - ay) * px + (ax - cx) * py + (cx * ay - ax * cy));
            u = (1 / det) * ((ay - bY) * px + (bx - ax) * py + (ax * bY - bx * ay));
			
			//security check only, could theoretically be deleted
            if (s >= 0 && t >= 0 && u >= 0)
            {
                return true;
            }
            return false;
        }
    }
	#endregion	

	
    #region Internal functions to create the triangle structure
	/// <summary>
	/// Create all possible triangles from the provided point set.
	/// Point set is stored in gObjects.
	/// </summary>
	void FindTriangle()
	{
		//counter counting all triangle number
		int x = 0;		
	
		//first point
		for (int a = 0; a < gObjects.Length-2; a++) {
			//second point
			for (int i = a + 1; i < gObjects.Length-1; i++) {
				//third point
				for (int j = i + 1; j < gObjects.Length; j++) {
					//line equation. Controlling if 3 point is on same line.
				    if (((gObjects[i].transform.position.z - gObjects[a].transform.position.z) * (gObjects[j].transform.position.x - gObjects[i].transform.position.x) - 
						 (gObjects[j].transform.position.z - gObjects[i].transform.position.z) * (gObjects[i].transform.position.x - gObjects[a].transform.position.x)) == 0) {
						//dont do anything
					}
					
					//finding points of triangle
					else {
						triangle[x].vertex1 = a;
						triangle[x].vertex2 = i;
						triangle[x].vertex3 = j;
						x ++;
				
					}
				}
			}
		}
		//Debug.Log("Found #triangle : "+x.ToString()); //DEBUG
	}
       
   
	
	/// <summary>
	/// Reads the CSV file containing the animation coordinates and names. Names have to be consistent with the editor
	/// </summary>	
	/// <param name='Filename'>
	/// Filename.
	/// </param>
	void ReadCSV(string Filename)
    {
        String csvFile;
		
		try
		{
			csvFile = File.ReadAllText(Filename);
		}
		catch
		{
			Debug.LogError("Could not open CSV file'"+Filename+"'!");
			csvFile = "";	
		}
						
		//split content at newline
        string[] lines = csvFile.Split(new string[] { Environment.NewLine }, StringSplitOptions.None);
		
        float [,] pointsTmp = new float[lines.Length, 3];
        string [] animationTmp = new string[lines.Length];
        
		//split all lines
        int validLines = 0; //count lines
        foreach (var line in lines)
        {
            string[] elements = line.Split(';');

            try {
                pointsTmp[validLines,0] = (float)Convert.ToDouble(elements[0], CultureInfo.GetCultureInfo("en-US").NumberFormat);
				pointsTmp[validLines,1] = (float)Convert.ToDouble(elements[1], CultureInfo.GetCultureInfo("en-US").NumberFormat);
				pointsTmp[validLines,2] = (float)Convert.ToDouble(elements[2], CultureInfo.GetCultureInfo("en-US").NumberFormat);
				animationTmp[validLines] = elements[3];
				
                validLines++;
            }
			//currently, invalid lines are ignored
            catch(Exception)
            {
				Debug.Log("Ignoring invalid line ("+ validLines + ") in file "+Filename);
            }
        }
		
		if(validLines == 0)
		{
			Debug.Log(" Warning: loaded empty CSV-File! : " + Filename + "\n");
			return;
		}
		
		
		//copy only for valid lines and store them in a game obejct structure
		gObjects = new GameObject[validLines]; //Total objects to store animations
		animationArray = new string[validLines];
        
		//over lines
		for (int j = 0; j < validLines; j++)
		{              			
			//over elements per line
			gObjects[j] = new GameObject();
	        gObjects[j].transform.position = new Vector3(pointsTmp[j,0], pointsTmp[j,1], pointsTmp[j,2]);
			animationArray[j] = animationTmp[j];
			
			/*for (int i = 0; i < 3; i++)TODEL
	        {                
	            points[j,i] = pointsTmp[j,i];
	        } */  
		}
    }
	
	/// <summary>
	/// Calculate binomeal cooeffient.
	/// </summary>
	int BinC(int n, int k)
	{
	    if (n < k)
	        return 0;		
	    // (n k) = n!/( k!*(n-k)! )
		return (int)(Factorial((ulong)n) / ( Factorial((ulong)k) * Factorial((ulong)(n - k))) );
	}

	/// <summary>
	/// Calculate factorial fucntion "n!"
	/// </summary>
	ulong Factorial(ulong n)
	{
	    ulong Result = 1;
	    for (ulong i = 1; i <= n; i++)
	    {
	        Result *= i;
	    }
	    return Result;
	}
	
    #endregion
	
	
	
		
}
