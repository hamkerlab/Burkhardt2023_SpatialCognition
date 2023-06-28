/**
@brief Central control class for an agent.
 
@details 
  - AgentScript is the control class for an agent. It is not intended
    that this class is directly attached to a 3D Object in Unity.
    Therefore the user must create a derived class for his scenario,
    where the behavior to protobuf messages can be overridden.
  - The agent could be either created directly in the scene or via a prefab. For how to create a prefab,  
    see the document <A HREF="../../VR-doc/agentPrefabs.pdf">agentPrefabs.pdf</a>. If you would like to create the agent
    directly in the scene, you have still to attach all scripts and fill all parameters which are described in the above file.
  - Camera positions for felice: 
    Left1 and Left2 = [-4.2, 84.5, 8]
    Right1 and Right2 = [+1.5, 84.5, 8]
  - Camera nearplanes: 0.6 to avoid problems with grasping

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Globalization;
using SimpleNetwork;

using UnityEngine;
using System.Collections;
using UnityEngine.AI;


public partial class AgentScript : MonoBehaviour
{
    #region Fields


    // SERVER VERSION
    public const string serverVersion = "1.0";

    /// <summary>
    /// The handles to the camera game object for displaying the images in the VR (Left)
    /// </summary>
    public Camera cameraLeft1;
    /// <summary>
    /// The handles to the camera game object for sending the images over TCP/IP network (Left)
    /// </summary>
    public Camera cameraLeft2;
    /// <summary>
    /// The handles to the camera game object for displaying the images in the VR (Right)
    /// </summary>
    public Camera cameraRight1;
    /// <summary>
    /// The handles to the camera game object for sending the images over TCP/IP network (Right)
    /// </summary>
    public Camera cameraRight2;
	/// <summary>
    /// The handles to the camera game object for sending the images over TCP/IP network (Right)
    /// </summary>
	public Camera MainCamera;
	public Camera MainCamera2;

    /// <summary>	
    /// Switch between different arrangements of the camera render textures
    /// </summary>
    protected int camViewMode;

    /// <summary>
    /// If true, display the cameras in the VR. Should only be set false if we have several agents in the scene.
    /// </summary>
    protected bool displayCameraVR = true;

    /// <summary>
    /// Default agentposition used in the reset function
    /// </summary>
    public Vector3 DefaultAgentPosition;

    /// <summary>
    /// The resolution of the left and right image, displayed on the VR screen
    /// </summary>
    protected int cameraDisplayWidth;
    /// <summary>
    /// The resolution of the left and right image, displayed on the VR screen
    /// </summary>
    protected int cameraDisplayHeight;

    /// <summary>
    /// Simple Networkinterfaces for the agent to listen for incomming connections and commands
    /// </summary>
    public SimpleNet MySimpleNet;

    /// <summary>
    /// Pan of left eye if not in LookAtMode
    /// </summary>
    protected float panLeft;

    /// <summary>
    /// Pan of right eye if not in LookAtMode
    /// </summary>
    protected float panRight;

    /// <summary>
    /// Tilt of the eyes if not in LookAtMode
    /// </summary>
    protected float tilt;

    /// <summary>
    /// HeadLookScript is looking at this point if we are not in the LookAtMode dependent on eye pan and tilt
    /// </summary>
    protected GameObject standardLookAtPoint;

    /// <summary>
    /// Position of agent before the last transposition
    /// </summary>
    protected Vector3 AgentLastPosition;

    /// <summary>
    /// Handle to the script that handles collisions of the agent
    /// </summary>
    protected ControllerCollider ControllerColliderScript;

    /// <summary>
    /// Direction of current movement in degree
    /// </summary>
    protected float DirectionOfMovement;

    /// <summary>
    /// How far the last movement should move the agent
    /// </summary>
    protected float GoalDistance;

    /// <summary>
    /// Script that controlls the body and head dependent on the eyes of the agent
    /// </summary>
    protected HeadLookController headLookScript;

    /// <summary>
    /// Progress of movement: if bigger or equal to GoalDistance, we arrived at the goal position
    /// </summary>
    // protected float DoneDistance = 0F;
    /// <summary>
    /// Set to true if the last movement is done
    /// </summary>
    protected bool IsCurrentMovementFinished = true;

    public bool getIsCurrentMovementFinished() { return this.IsCurrentMovementFinished; }
    /// <summary>
    /// ID of current movement
    /// </summary>
    protected int MovementIDExecuting;



    /// <summary>
    /// Start vector/point of current movement
    /// </summary>
    protected Vector3 startPoint;

    /// <summary>
    /// Set to true if the agent got a command to look at one position
    /// </summary>
    private bool EyeMovementInLookAtMode = false;

    // Max tilt for MoveEyes()
    private float maxTilt = 90f;
    // Max Pan for MoveEyes()
    private float maxPan = 135f;

    /// <summary>
    /// ID of current eye movement
    /// </summary>
    protected int EyeIDExecuting;


    public enum ArmMsg { ArmMsgNone, ArmMsgGrasp, ArmMsgPoint, ArmMsgInteraction };
    /// <summary>
    /// Indicates the type of the last message which is grasping (1), pointing (2), interacting (3) with the environment.
    /// </summary>
    protected ArmMsg lastArmMsg = ArmMsg.ArmMsgNone;


    /// <summary>
    /// ID of arm action
    /// </summary>
    protected int ArmIDExecuting;

    /// <summary>
    /// The right hand. Reference is automatically created by script HandCollider.cs.
    /// </summary>
    protected GameObject rightHand;

    /// <summary>
    /// The gameobject which the agent is currently grasping in its right hand. If no object is grasped, null. Reference is automatically set by script HandCollider.cs.
    /// </summary>
    protected GameObject rightGraspedObject = null;

    /// <summary>
    /// Point to look at, if in LookAtMode
    /// </summary>
    private Vector3 LookAtTarget;

    /// <summary>
    /// Point to look at used for a saccade
    /// </summary>
    Vector3 newLookAtTarget;

    /// <summary>
    /// The default rotation of the agent: angle of rotation in degree around the y-axis
    /// </summary>
    public float DefaultRotation;

    /// <summary>
    /// If set to true, the agent sends continuously his location
    /// </summary>
    public bool SendGridPosition = true;

    /// <summary>
    /// If set to true, the agent sends continuously eye information
    /// </summary>
    private bool SendEyePosition = true;
	
	/// <summary>
    /// If set to true, the agent sends continuously eye information
    /// </summary>
    private bool SendObjectPosition = true;

    /// <summary>
    /// If set to true, the agent sends continuously balance information
    /// </summary>
    private bool SendHeadMotion = false;

    /// <summary>
    /// If set to true, the agents sends continuous images of his view
    /// </summary>
    private bool SendImages = false;

    /// <summary>
    /// Asynchronous (false) or synchronous (true) mode
    /// </summary>
    protected bool SyncMode = false;

    /// <summary>
    /// Time since last image was send in seconds
    /// </summary>
    private float TimeSinceLastImageWasSend = 0F;
    // Variables for render the images
    public Texture2D tex;
    public RenderTexture rt_R;
    public RenderTexture rt_L;
	public RenderTexture rt_M;
    public Texture2D tex_R;
    public Texture2D tex_L;
	public Texture2D tex_M;

    private bool ResetCalledAtStart = false;


    /// <summary>
    /// True if in the first frame was already sent to prevent double sending.
    /// </summary>
    private bool msgStartSyncAlreadySended = false;

    /// <summary>
    /// The simulation times unit in seconds. Precisely, the time between two send time points of the images. In synchronous mode, 
    /// the sending is always executed in the first frame, therefore it is the simulated time of 2 frames. In asychron mode, we wait at least "SimulationTimePerFrame" seconds
    /// to send an image, hence this is independent of the number of frames passed.
    /// </summary>
    protected float SimulationTimePerFrame = 0.1f;
    /// <summary>
    /// The width of the on screen images
    /// </summary>
    protected int ImageResolutionWidth = 128;
    /// <summary>
    /// The height of the on screen images
    /// </summary>
    protected int ImageResolutionHeight = 128;

    /// <summary>
    /// Horizontal field of view in degree
    /// </summary>
    protected float FovHorizontal = 120f;
    /// <summary>
    /// Vertical field of view in degree
    /// </summary>
    protected float FovVertical = 90f;

    /// <summary>
    /// Agent is moved that much between calls of the Updatefunction - some kind of speed measurement
    /// </summary>	
    public float CurrentMovementSpeed = 0.0f;

    /// <summary>
    /// Maximum speed of agent
    /// </summary>
    protected float MovementSpeed = 1.0f;

    /// <summary>
    /// Should the agent stop its movement?
    /// </summary>
    public bool movementCanceled = false;

    /// <summary>
    /// Timout in seconds
    /// </summary>
    protected float SyncModeFrameTimeOut = 3.0f;

    /// <summary>
    /// Worker class to do the interpolation
    /// </summary>
    public InterpolateAnimations interpolateAnimations;

    /// <summary>
    /// If we get a graspPos msg, we could draw a line of the left eye to the grasp point for debugging. This is stored by this 3D object.
    /// </summary>
    GameObject debugLine = null;

    /// <summary>
    /// Each walk animation has a specific speed, which looks good for a specific MovementSpeed.
    /// </summary>
    protected float GoodWalkAnimationSpeed = 1.5f;
    protected float GoodWalkAnimationSpeedVideo = 0.0013f;


    // Balance information for velocity and acceleration computation
    Vector3 lastFrameEyeRotation;
    Vector3 lastFrameRotation;
    Vector3 lastFramePosition;
    Vector3 lastFrameRotationVelocity;
    Vector3 lastFrameVelocity;

    // Saccade parameters
    public float Speed = 1f; // Display Speed (1 = normal Speed)
    public float eps = 0.01f;
    public float saccTime = 0; // Runtime of current saccade
    public float saccTimeDone = 0; // Time done of current saccade
    public bool saccadeActive = false; // Boolflag for active saccade
    public float m0 = 7f;
    public float vpkL = 0, vpkR = 0;
    public float RL = 0, RR = 0, A = 0;
    public float vL = 0, vR = 0;
    public float EccL = 0, EccR = 0;
    public Vector3 curDirL, curDirR, tarDirL, tarDirR; // Current direction and target direction of left and right camera
	public Vector3 nTargL, nTargR, fixL, fixR; //normalized Vectors of Target left and rigth
    public bool flag = false; // flag for the saccFlag message. If true, it changes the saccade to linear
    
    // New navigation stuff
    public NavMeshAgent agent; // navigating agent for Unity built in navogation
    public bool allowClickNavigation = true; // right clicking in game tab lets you navigate the agent
    public bool makeVideo = true;
	public bool syncContinue; // for video creation, is sent by the python client once it is finished with the previous image
	
	#endregion Fields

    #region PublicMethods


    /// <summary>
    /// Determines if we should send a startSync (in the first frame) or stopSync (in the second frame).
    /// </summary>
    protected enum FrameState
    {
        FirstFrame,
        SecondFrame
    };
    /// <summary>
    /// Determines if we should send a startSync (in the first frame) or stopSync (in the second frame).
    /// </summary>
    protected FrameState frameState;

    /// <summary>
    /// Agent ID, starting from 0
    /// </summary>
    public int AgentID = 0;


    /// <summary>
    /// Flag for controlling walking animation. True if we walk, hence if a walking animation has to be played.
    /// </summary>
    protected bool walking = false;
    public CSVReader csvReaderAnim;
    protected List<string> ArmAnimationList = new List<string>();
    protected bool IsArmAnimationExecuted
    {
        get;
        set;
    }

    /*
    public void InitializeGraspActionExecutionMessageSending()
    {
        IsGraspAnimationExecuted = true;		
    }
    */
    protected string[] getGraspAnimationsBeeingExecuted()
    {
        // List of animation names with aren't a grasp animation
        // List<string> exceptions = (new string[] { "walk" }).ToList();

        List<string> graspAnimationsPlaying = new List<string>();

        foreach (string name in ArmAnimationList)
        {
            if (gameObject.GetComponent<Animation>().IsPlaying(name))
            {
                graspAnimationsPlaying.Add(name);
                // Debug.Log("Animation playing: " + name );
            }
        }

        return graspAnimationsPlaying.ToArray();
    }

    protected void TestGraspAnimations()
    {
        if (IsArmAnimationExecuted) return;

        string[] graspAnimationsPlaying = getGraspAnimationsBeeingExecuted();

        if (graspAnimationsPlaying.Length > 0)
        {
            IsArmAnimationExecuted = true;
        }

    }

    protected void GraspActionExecutionMessageSending()
    {

        if (IsArmAnimationExecuted)
        {
            string[] graspAnimationsPlaying = getGraspAnimationsBeeingExecuted();



            if (graspAnimationsPlaying.Length > 0)
            {
                if (MySimpleNet != null)
                {
                    MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = ArmIDExecuting, status = MsgActionExecutionStatus.InExecution });

                }


            }

            // Animation was sucessfully finished
            else
            {

                if (debugLine != null)
                    Destroy(debugLine);

                if (MySimpleNet != null)
                {
                    MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = ArmIDExecuting, status = MsgActionExecutionStatus.Finished });

                }

                IsArmAnimationExecuted = false;
            }

        }

    }

    /// <summary>
    /// Initializes agent from cConfiguration object. This function is called from BehaviourScript or from derived classes. 
    /// Current procedure is for an single agent:
    /// - Create SimpleNet
    /// - Get all information from the config-file
    /// - Initialise camera related variables
    /// </summary>
    /// <param name='config'>
    /// cConfiguration object
    /// </param>
    /// <param name='localIP'>
    /// IP of the local pc.
    /// </param>
    /// <param name='ipPortOffset'>
    /// IP port offset, starting from 0 for the first agent.
    /// </param>
    /// /
    public virtual void InitializeFromConfiguration(cConfiguration config, string localIP, int ipPortOffset)
    {
        Debug.Log("Init agent" + ipPortOffset + " with: " + localIP + ":" + (config.LocalPort + ipPortOffset + 1));
        camViewMode = 0;

        // SimpleNet
        // config.LocalPort => Port for behaviourScript
        // config.LocalPort + 1 => Port for the first agent
        this.MySimpleNet = new SimpleNet(localIP, config.LocalPort + ipPortOffset + 1);

        // Config 
        this.SyncMode = config.SyncMode;
        this.makeVideo = config.MakeVideo;
        this.SimulationTimePerFrame = config.SimulationTimePerFrame;
        this.ImageResolutionWidth = config.ImageResolutionWidth;
		this.ImageResolutionHeight = config.ImageResolutionHeight;
        this.SendGridPosition = config.SendGridPosition;
        this.MovementSpeed = config.MovementSpeed;
        this.cameraDisplayWidth = config.CameraDisplayWidth;
		this.FovVertical = config.FovVertical;
		this.FovHorizontal = config.FovHorizontal;
		
        cameraDisplayHeight = Mathf.RoundToInt(cameraDisplayWidth * ImageResolutionHeight / ImageResolutionWidth);
		Debug.Log("CameraHeight = " + cameraDisplayHeight);

        cameraLeft1.fieldOfView = FovVertical;
        cameraLeft2.fieldOfView = FovVertical;

        cameraRight1.fieldOfView = FovVertical;
        cameraRight2.fieldOfView = FovVertical;

        // Enable or display cameras
        setDisplayCameraVR(this.displayCameraVR);

        Debug.Log("ImageResolutionWidth = " + ImageResolutionWidth);
        Debug.Log("ImageResolutionHeight = " + ImageResolutionHeight);
        Debug.Log("FOV Horizontal = " + FovHorizontal);
		Debug.Log("FOV Vertical = " + FovVertical);

        // Set up camera render objects
        tex_L = new Texture2D(ImageResolutionWidth, ImageResolutionHeight, TextureFormat.RGB24, true);
        tex_R = new Texture2D(ImageResolutionWidth, ImageResolutionHeight, TextureFormat.RGB24, true);
		tex_M = new Texture2D(ImageResolutionWidth, ImageResolutionHeight, TextureFormat.RGB24, true);
        
		rt_R = new RenderTexture(ImageResolutionWidth, ImageResolutionHeight, 24);
        rt_L = new RenderTexture(ImageResolutionWidth, ImageResolutionHeight, 24);
		rt_M = new RenderTexture(ImageResolutionWidth, ImageResolutionHeight, 24);
        
		rt_R.useMipMap = true;
        rt_L.useMipMap = true;
		rt_M.useMipMap = true;
        
		cameraRight2.GetComponent<Camera>().targetTexture = rt_R;
        cameraLeft2.GetComponent<Camera>().targetTexture = rt_L;
		MainCamera2.GetComponent<Camera>().targetTexture = rt_M;

        string filename = "Assets/animations/" + gameObject.name + ".csv";
        if (File.Exists(filename))
            csvReaderAnim = new CSVReader(filename);
        else
            Debug.Log("Object coordinate file for agent " + gameObject.name + " is not existing\n");

    }

    /// <summary>
    /// Resets the agent
    /// </summary>
    public void AgentReset()
    {
        // Do not move anymore
        this.CurrentMovementSpeed = 0.0F;
        IsArmAnimationExecuted = false;

        // Stop the agent's NavMesh movement
        agent.isStopped = true;
        agent.ResetPath(); 

        if (this.IsCurrentMovementFinished == false)
        {
            IsCurrentMovementFinished = true;
            // We aborted a running movement, signal that
            Debug.Log("Agent Reset");
            MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = MovementIDExecuting, status = MsgActionExecutionStatus.Aborted });
        }

        // Reset the position of the agent object
        gameObject.transform.position = DefaultAgentPosition;
        AgentLastPosition = DefaultAgentPosition;

        // Maybe this will cause some bad behaviour; i don't know
        gameObject.transform.rotation = Quaternion.Euler(0, DefaultRotation, 0);

        // Reset the eyes
        EyesDirectionReset();
    }

    /// <summary>
    /// Function for the animation system
    /// </summary>
    /// <returns></returns>
    public float GetSpeed()
    {
        return this.CurrentMovementSpeed;
    }

    /// <summary>
    /// Initializes and starts the saccade
    /// </summary>
    /// <param name="Target"> Target point of the saccade </param>
    void startSaccade(float panL, float panR, float tilt, Vector3 Target)
	{
		// Turn cameras/eyes to the point
		saccTime = 1f/Speed;
		newLookAtTarget = Target;
	
		fixL = new Vector3(cameraLeft1.transform.eulerAngles.x, cameraLeft1.transform.eulerAngles.y,0); 
		fixR = new Vector3(cameraRight1.transform.eulerAngles.x, cameraRight1.transform.eulerAngles.y,0);
		
		Vector3 currDir = new Vector3(Mathf.Tan(fixL.y*Mathf.PI/180),Mathf.Tan(fixL.x*Mathf.PI/180),1);
		Debug.Log("currDir = " + currDir);
		
		Vector3 targetL = currDir - new Vector3(Mathf.Tan(tilt*Mathf.PI/180), Mathf.Tan(panL*Mathf.PI/180), 0);
		Vector3 targetR = currDir - new Vector3(Mathf.Tan(tilt*Mathf.PI/180), Mathf.Tan(panR*Mathf.PI/180), 0);
		
		RL = Vector3.Angle(currDir,targetL);
		RR = Vector3.Angle(currDir,targetR);
		
		Debug.Log("RL = " + RL);
		Debug.Log("RR = " + RR);
			
		// calculate peak velocity
		vpkL = 750*(1-Mathf.Exp(-RL/16))+50; 
		vpkR = 750*(1-Mathf.Exp(-RR/16))+50;

		// direction of target 
		nTargL = Vector3.Normalize(new Vector3(-Mathf.Tan(tilt*Mathf.PI/180),Mathf.Tan (panLeft*Mathf.PI/180),0));
		nTargR = Vector3.Normalize(new Vector3(-Mathf.Tan(tilt*Mathf.PI/180),Mathf.Tan (panRight*Mathf.PI/180),0));
		
		//reset saccade time
		saccTime = 0; 
		saccadeActive = true;
	}

    /// <summary>
    /// Makes the agent look at a position with head and eyes
    /// </summary>
    /// <param name="Target"> Target point of the saccade </param>

    /*public virtual void LookAtPoint (Vector3 Target)
    {
        //now we are in mode to fixate (LookAtPointMode)
        EyeMovmentInLookAtMode = true;

        // Make upper body lean to the point
        headLookScript.target = Target;

        //turn cameras/eyes to the point
        cameraLeft1.transform.LookAt (Target);
        cameraRight1.transform.LookAt (Target);
        cameraLeft2.transform.LookAt (Target);
        cameraRight2.transform.LookAt (Target);
        //remember the point for later adjustments
        LookAtTarget = Target;
    } */
    
	
	public virtual void LookAtPoint(Vector3 Target)
    {
        if (LookAtTarget != Target)
        {
            // Make upper body lean to the point
            headLookScript.target = Target;
			
			Debug.Log("!!!!!!! CHECK LookAtPoint !!!!!!!");
            startSaccade(0,0,0, Target);
        }

        // Now we are in mode to fixate (LookAtPointMode)
        EyeMovementInLookAtMode = true;
    }
	

    /// <summary>
    /// Turns off LookAtMode and adds rotations to the cams relative to the player figure (not relativ to the head)
    /// </summary>
    /// <param name="deltaPanLeft">Pan of left Eye</param>
    /// <param name="deltaPanRight">Pan of right Eye</param>
    /// <param name="deltaTilt">Tilt of both Eyes</param>
    public virtual void MoveEyes(float deltaPanLeft, float deltaPanRight, float deltaTilt)
	{

		///We have two modes. In one mode, we look at one point in the world. And another one
		///handled in this function, the MoveEye (relative to Body) mode.
		///We rotate the eye cameras. But the script, that controlls the body rotation, needs
		///a point to look at(standardLookAtPoint), so we rotate an invisible object around the head, too. Then
		///we look at the coordinates of this object. Now the movements look good, too.

		// No longer in mode to fixate (LookAtPointMode)
		EyeMovementInLookAtMode = false;

		// Adjust tilt and pans
		tilt += deltaTilt;
		panLeft += deltaPanLeft;
		panRight += deltaPanRight;
		
		// Constraint to maximum pan/tilt values
        if(tilt < -maxTilt)
        	tilt = -maxTilt;
        if(tilt > maxTilt)
        	tilt = maxTilt;
        if(panLeft < -maxPan)
        	panLeft = -maxPan;
        if(panLeft > maxPan)
        	panLeft = maxPan;
        if(panRight < -maxPan)
        	panRight = -maxPan;
        if(panRight > maxPan)
        	panRight = maxPan;

		// Rotate cams
		// * is the overlodaded operator for sequential execution of the rotations. It is NOT a multiplication!
		/*cameraLeft1.transform.rotation = gameObject.transform.rotation * Quaternion.AngleAxis (panLeft, Vector3.up) * Quaternion.AngleAxis (tilt, Vector3.left);
		cameraRight1.transform.rotation = gameObject.transform.rotation * Quaternion.AngleAxis (panRight, Vector3.up) * Quaternion.AngleAxis (tilt, Vector3.left);
		cameraLeft2.transform.rotation = gameObject.transform.rotation * Quaternion.AngleAxis (panLeft, Vector3.up) * Quaternion.AngleAxis (tilt, Vector3.left);
		cameraRight2.transform.rotation = gameObject.transform.rotation * Quaternion.AngleAxis (panRight, Vector3.up) * Quaternion.AngleAxis (tilt, Vector3.left);*/
		
		Vector3 middle = 0.5f*(cameraLeft1.transform.position - cameraRight1.transform.position) + cameraLeft1.transform.position;				
		/*cameraLeft1.transform.RotateAround(cameraLeft1.transform.position, cameraLeft1.transform.up, panLeft);
		cameraLeft2.transform.RotateAround(cameraLeft2.transform.position, cameraLeft2.transform.up, panLeft);
		cameraRight1.transform.RotateAround(cameraRight1.transform.position, cameraRight1.transform.up, panRight);
		cameraRight2.transform.RotateAround(cameraRight2.transform.position, cameraRight2.transform.up, panRight);
		
		cameraLeft1.transform.RotateAround(cameraLeft1.transform.position, cameraLeft1.transform.right, tilt);
		cameraLeft2.transform.RotateAround(cameraLeft2.transform.position, cameraLeft2.transform.right, tilt);
		cameraRight1.transform.RotateAround(cameraRight1.transform.position, cameraRight1.transform.right, tilt);
		cameraRight2.transform.RotateAround(cameraRight2.transform.position, cameraRight2.transform.right, tilt);*/
		
		// Rotate the StandardLookAtPoint, so that the head looks in the average Direction of Both Eyes;
		standardLookAtPoint.transform.RotateAround (middle,  gameObject.transform.right, -deltaTilt);
		standardLookAtPoint.transform.RotateAround (middle,  gameObject.transform.up, (deltaPanLeft+deltaPanRight)/2.0f );
		// Turn head in that direction now
		headLookScript.target = standardLookAtPoint.transform.position;
		
		startSaccade(deltaPanLeft, deltaPanRight, deltaTilt, headLookScript.target);
	}

    /// <summary>
    /// Executed when VR is shut down
    /// </summary>
    public void OnApplicationQuit()
    {
        // Shut down the networkinterface gracefully
        if (MySimpleNet != null)
        {
            MySimpleNet.Stop();
        }
    }

    /// <summary>
    /// Yeppi, agent did get pleasure and reward ;D .
    /// Sends a message over the Network
    /// </summary>
    /// <param name="Reward">value</param>
    public void ReceiveReward(float Reward)
    {
        MySimpleNet.Send(new MsgReward() { reward = Reward });
    }

    /// <summary>
    /// Saves images of both views of this agent. Deactivated as the current implementation is obsolet (TODO with port to unity 4.x)
    /// </summary>
    public void SaveViewPNG()
    {
        // Texture2D EyeRightTexture = GetCameraViewTexture(cameraRight2);
        // Texture2D EyeLeftTexture = GetCameraViewTexture(cameraLeft2);
        /*
                byte[] bytesRight = GetCameraViewTexture(cameraRight2).EncodeToPNG();
                Debug.Log("---SavedView.png--- unter :" + Application.dataPath.ToString());
                File.WriteAllBytes(Application.dataPath + "/SavedViewRight.png", bytesRight);
                // Destroy(EyeRightTexture);

                byte[] bytesLeft = GetCameraViewTexture(cameraLeft2).EncodeToPNG();
                Debug.Log("---SavedView.png--- unter :" + Application.dataPath.ToString());
                File.WriteAllBytes(Application.dataPath + "/SavedViewLeft.png", bytesLeft);
                */
        // Destroy(EyeLeftTexture);
    }

    /// <summary>
    /// Sends a click on a menu item to the agent.
    /// Sends an message over the Network.
    /// </summary>
    /// <param name="menuID">id of the menu</param>
    public void SendMenuClick(int menuID)
    {
        MySimpleNet.Send(new MsgMenu() { eventID = menuID });
    }

    #endregion PublicMethods

    #region ProtectedMethods

    /// <returns> distance traveled </returns>
    protected float GetDoneDistance()
    {
        return Vector3.Distance(startPoint, gameObject.transform.position);
    }



    /// <summary>
    /// Initiates a new movement sequence.
    /// </summary>
    /// <param name='MsgMove'>
    /// Move message
    /// </param>
    protected virtual void StartNewMovement(MsgAgentMovement MsgMove)
    {

        if (this.IsCurrentMovementFinished == false)
        {
            // We aborted a running movement, send a signal	
            Debug.Log("Stopped new movement, as an old movement is running...");
            MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = MovementIDExecuting, status = MsgActionExecutionStatus.Aborted });

        }

        // Save the Informations needed for execution
        this.MovementIDExecuting = MsgMove.actionID;
        this.GoalDistance = MsgMove.distance;
        this.DirectionOfMovement = MsgMove.degree;
        this.AgentLastPosition = gameObject.transform.position;
        this.IsCurrentMovementFinished = false;
        this.startPoint = gameObject.transform.position;
        // Turn agentfigure in direction of movement
        gameObject.transform.localRotation = Quaternion.identity;
        gameObject.transform.Rotate(0, DirectionOfMovement, 0);
    }

    /// <summary>
    /// Initiates a new movement sequence (old version independent of MsgAgentMovement).
    /// </summary>
    public virtual void StartNewMovement(float distance, float degree)
    {
        if (this.IsCurrentMovementFinished == false)
        {
            // We aborted a running movement, send a signal
            Debug.Log("Aborted new movement, as I'm still walking");
            MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = MovementIDExecuting, status = MsgActionExecutionStatus.Aborted });
        }
				
		Debug.Log("New movement ...");
        // Save the Informations needed for execution
        this.MovementIDExecuting = MovementIDExecuting + 1; //MsgMove.actionID;
        this.GoalDistance = distance;
        this.DirectionOfMovement = degree;
        this.AgentLastPosition = gameObject.transform.position;
        this.IsCurrentMovementFinished = false;
        this.startPoint = gameObject.transform.position;
		
		// Turn agentfigure in direction of movement 
        gameObject.transform.localRotation = Quaternion.identity;
        gameObject.transform.Rotate(0, DirectionOfMovement, 0);
    }

    /// <summary>
    /// Resets eyes and cameras
    /// </summary>
    protected virtual void EyesDirectionReset()
    {
		// Reset cameras back to the standard direction
        // Align the cameras like the parent object (which should be in this case the head or body of the agent)
        cameraLeft1.transform.localRotation = Quaternion.identity;
        cameraLeft2.transform.localRotation = Quaternion.identity;
        cameraRight1.transform.localRotation = Quaternion.identity;
        cameraRight2.transform.localRotation = Quaternion.identity;



        // Reset the StandardLookAtPointObject and therefore the head direction
        if (headLookScript != null)
            headLookScript.target = standardLookAtPoint.transform.position;

        // We are not in mode to fixate (LookAtPointMode)
        EyeMovementInLookAtMode = false;

        // Eyes are straight on
        panLeft = 0;
        panRight = 0;
        tilt = 0;

        if (standardLookAtPoint != null)
            standardLookAtPoint.transform.position = CalculateStandardLookAtPointPosition();
    }

    /// <summary>
    /// Moves the agent figure in the VR
    /// </summary>
    /// <param name="angle">angle relativ to the World</param>
    /// <param name="distance">distance to move</param>
    /// <returns>CollisionFlag</returns>
    protected virtual CollisionFlags MoveAgent(float angle, float distance)
    {
        // We need the angle in radian
        angle = angle * (Mathf.PI / 180);
        // Calculate the translation and move the agent
        return gameObject.GetComponent<CharacterController>().Move(
            new Vector3(
                ((Mathf.Sin(angle) * distance)),
                0,
                (Mathf.Cos(angle) * distance)));
    }

    /// <summary>
    /// Behavior function for MsgVersionCheck
    /// </summary>
    /// <param name="msg">MsgAgentEyeFixation object</param>
    protected virtual void ProcessMsgVersionCheck(MsgVersionCheck msg)
    {
        if (MySimpleNet != null)
        {
            MySimpleNet.Send(new MsgVersionCheck() { version = serverVersion });
        }

    }



    /// <summary>
    /// Behavior function for MsgAgentEyeFixation  (should be overridden in a derived class)
    /// </summary>
    /// <param name="msg">MsgAgentEyeFixation object</param>
    protected virtual void ProcessMsgAgentEyeFixation(MsgAgentEyeFixation msg)
    {
        if (MySimpleNet != null)
        {
            MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = EyeIDExecuting, status = MsgActionExecutionStatus.InExecution });
        }
        LookAtPoint(new Vector3(msg.targetX, msg.targetY, msg.targetZ));
    }

    /// <summary>
    /// Behavior function for MsgAgentEyeMovment (should be overridden in a derived class)
    /// </summary>
    /// <param name="msg">MsgAgentEyemovement object</param>
    protected virtual void ProcessMsgAgentEyeMovement(MsgAgentEyemovement msg)
    {
        MoveEyes(msg.panLeft, msg.panRight, msg.tilt);
    }

    //ProcessMsgAgentGraspID => see region Animation and grasping
    //ProcessMsgAgentGraspPos => see region Animation and grasping


    /// <summary>
    /// Behavior function for MsgAgentPointID (should be overridden in a derived class)
    /// </summary>
    /// <param name="msg">MsgAgentPointID object</param>
    protected virtual void ProcessMsgAgentPointID(MsgAgentPointID msg)
    {
        Debug.Log(String.Format("AgentPointID received ({0:d})",
                        msg.objectID));
    }

    /// <summary>
    /// Behavior function for MsgAgentPointPos (should be overridden in a derived class)
    /// </summary>
    /// <param name="msg">MsgAgentPointPos object</param>
    protected virtual void ProcessMsgAgentPointPos(MsgAgentPointPos msg)
    {
        Debug.Log(String.Format("AgentPointPos received ({0:f},{1:f})",
                        msg.targetX,
                        msg.targetY));
    }

    /// <summary>
    /// Behavior function for MsgAgentInteractionID (should be overridden in a derived class)
    /// </summary>
    /// <param name="msg">MsgAgentInteractionID object</param>
    protected virtual void ProcessMsgAgentInteractionID(MsgAgentInteractionID msg)
    {
        Debug.Log(String.Format("AgentInteractionID received ({0:d})",
                        msg.objectID));
    }

    /// <summary>
    /// Behavior function for MsgAgentInteractionPos (should be overridden in a derived class)
    /// </summary>
    /// <param name="msg">MsgAgentInteractionPos object</param>
    protected virtual void ProcessMsgAgentInteractionPos(MsgAgentInteractionPos msg)
    {
        Debug.Log(String.Format("AgentInteractionPos received ({0:f},{1:f})",
                        msg.targetX,
                        msg.targetY));
    }

    /// <summary>
    /// Behavior function for MsgAgentMovement (should be overridden in a derived class)
    /// </summary>
    /// <param name="msg">MsgAgentMovement object</param>
    protected virtual void ProcessMsgAgentMovement(MsgAgentMovement msg)
    {
        // Debug.Log("StartNewMovement (msg);"); //TODEL
        StartNewMovement(msg);
    }

    /// <summary>
    /// Behavior function for receiving the ANNarchy network structure (should be overridden in a derived class). In this case, the flag is MsgAnnarNetwork-Update = false.
    /// </summary>
    /// <param name="msg">MsgAnnarNetwork object</param>    
    protected virtual void ProcessMsgAnnarNetwork(AnnarNetwork msg)
    {
        Debug.Log(String.Format("AnnarNetwork object received"));
    }

    /// <summary>
    /// Behavior function for receiving the firing rates and membrane potential (should be overridden in a derived class). In this case, the flag is MsgAnnarNetwork-Update = true.
    /// </summary>
    /// <param name="msg">MsgAnnarNetwork object</param>    
    protected virtual void ProcessMsgAnnarUpdateRates(AnnarNetwork msg)
    {
        Debug.Log(String.Format("AnnarNetwork update received"));
    }

    #endregion ProtectedMethods

    /// <summary>
    /// Calculates the SLP (standard look at point) position. This is the point 10 units in front of the agent. Precisely, it is 
    /// the averaged looking direction of left and right eye, originating from the point between the two eyes.
    /// </summary>
    /// <returns>
    /// The SLP position.
    /// </returns>
    private Vector3 CalculateStandardLookAtPointPosition()
    {
        // Calculate position for standardLookAtPoint
        Vector3 cL = cameraLeft1.transform.position;
        Vector3 cR = cameraRight1.transform.position;
        Vector3 c = cR - cL;
        Vector3 n = new Vector3(-c.z, 0, c.x);
        Vector3 pos = cL + (0.5f * c) + 10 * c.sqrMagnitude * n.normalized;
        // Debug.Log(c.sqrMagnitude);
        return pos;
    }



    /// <summary>
    /// Unity does not allow conventional constructors, but provides this function for initialisations.
    /// </summary>
    void Awake()
    {

        if (this.enabled)
        {
            // Initializations
            headLookScript = gameObject.GetComponent<HeadLookController>();

            this.ControllerColliderScript = gameObject.GetComponent<ControllerCollider>();

            frameState = FrameState.FirstFrame;
            IsArmAnimationExecuted = false;

            standardLookAtPoint = new GameObject();

            // Set a red sphere as the standardLookAtPoint for testing
            // standardLookAtPoint = Instantiate(Resources.Load("RedSphere") as UnityEngine.Object, new Vector3(0, 0, 0), Quaternion.identity) as GameObject;

            standardLookAtPoint.transform.parent = gameObject.transform;
            standardLookAtPoint.transform.position = CalculateStandardLookAtPointPosition();

            // For animations			
            interpolateAnimations = new InterpolateAnimations(this, "Assets/animations/feliceGraspTarget.csv");
            ArmAnimationList = ArmAnimationList.Union(interpolateAnimations.animationArray.ToList()).ToList();

            // All other resets have to be done later because:
            // 1) after behaviourScript-awake: anything that is related to runtime spawning of agent like
            //    this.AgentReset ()
            //    => this part is execute at runtime in the first call agent.update()
            // 2) after loading the config file (see InitializeFromConfiguration(), like
            //    init rendertexture
            //    => this part is called by behaviourscript::awake()

        }
    }


    /// <summary>
    /// Main routine to process incoming message.
    /// </summary>
    void ProcessMsg(MsgObject NextMsg)
    {
        // Check if client requests server version
        if (NextMsg.msgVersionCheck != null)
        {
            ProcessMsgVersionCheck(NextMsg.msgVersionCheck);
        }

        // Test if message is grasp/interaction msg: if yes, abort the old one
        if ((NextMsg.msgAgentGraspPos != null) ||
            (NextMsg.msgAgentGraspID != null) ||
            (NextMsg.msgAgentPointPos != null) ||
            (NextMsg.msgAgentPointID != null) ||
            (NextMsg.msgAgentInteractionID != null) ||
            (NextMsg.msgAgentInteractionPos != null))
        {
            if (IsArmAnimationExecuted)
            {

                if (debugLine != null)
                    Destroy(debugLine);

                if (MySimpleNet != null)
                {
                    MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = ArmIDExecuting, status = MsgActionExecutionStatus.Aborted });
                }
                IsArmAnimationExecuted = false;
            }

        }



        // New movementcommand
        if (NextMsg.msgAgentMovement != null)
        {
            ProcessMsgAgentMovement(NextMsg.msgAgentMovement);
        }

        if (NextMsg.msgAgentGraspPos != null)
        {
            lastArmMsg = ArmMsg.ArmMsgGrasp;
            // Send failure to agent if already an object was grasped
            if (rightGraspedObject != null)
            {
                if (MySimpleNet != null)
                {
                    MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = NextMsg.msgAgentGraspPos.actionID, status = MsgActionExecutionStatus.Aborted });
                }
            }
            else
            {
                ArmIDExecuting = NextMsg.msgAgentGraspPos.actionID;
                ProcessMsgAgentGraspPos(NextMsg.msgAgentGraspPos);
            }

        }
        if (NextMsg.msgAgentGraspID != null)
        {
            lastArmMsg = ArmMsg.ArmMsgGrasp;
            // send failure to agent if already an object was grasped
            if (rightGraspedObject != null)
            {
                if (MySimpleNet != null)
                {
                    MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = NextMsg.msgAgentGraspID.actionID, status = MsgActionExecutionStatus.Aborted });
                }
            }
            else
            {
                ArmIDExecuting = NextMsg.msgAgentGraspID.actionID;
                ProcessMsgAgentGraspID(NextMsg.msgAgentGraspID);
            }

        }
        if (NextMsg.msgAgentPointPos != null)
        {
            lastArmMsg = ArmMsg.ArmMsgPoint;
            ArmIDExecuting = NextMsg.msgAgentPointPos.actionID;
            ProcessMsgAgentPointPos(NextMsg.msgAgentPointPos);

        }
        if (NextMsg.msgAgentPointID != null)
        {
            lastArmMsg = ArmMsg.ArmMsgPoint;
            ArmIDExecuting = NextMsg.msgAgentPointID.actionID;
            ProcessMsgAgentPointID(NextMsg.msgAgentPointID);

        }
        if (NextMsg.msgAgentInteractionID != null)
        {
            lastArmMsg = ArmMsg.ArmMsgInteraction;
            ArmIDExecuting = NextMsg.msgAgentInteractionID.actionID;
            ProcessMsgAgentInteractionID(NextMsg.msgAgentInteractionID);

        }
        if (NextMsg.msgAgentInteractionPos != null)
        {
            lastArmMsg = ArmMsg.ArmMsgInteraction;
            ArmIDExecuting = NextMsg.msgAgentInteractionPos.actionID;
            ProcessMsgAgentInteractionPos(NextMsg.msgAgentInteractionPos);

        }
        // Make the agent constantly look to one Point command!
        if (NextMsg.msgAgentEyeFixation != null)
        {
            EyeIDExecuting = NextMsg.msgAgentEyeFixation.actionID;
            ProcessMsgAgentEyeFixation(NextMsg.msgAgentEyeFixation);
        }

        // Make the Eyes constantly look in directions relative to the agentdirection!
        if (NextMsg.msgAgentEyemovement != null)
        {
            EyeIDExecuting = NextMsg.msgAgentEyemovement.actionID;
            ProcessMsgAgentEyeMovement(NextMsg.msgAgentEyemovement);
        }

        if (NextMsg.msgAgentGraspRelease != null)
        {
            ArmIDExecuting = NextMsg.msgAgentGraspRelease.actionID;
            ProcessMsgGraspRelease(NextMsg.msgAgentGraspRelease);
        }
        if (NextMsg.msgAgentTurn != null)
        {
            MovementIDExecuting = NextMsg.msgAgentTurn.actionID;
            ProcessMsgAgentTurn(NextMsg.msgAgentTurn);
        }

        if (NextMsg.msgAgentMoveTo != null)
        {
            MovementIDExecuting = NextMsg.msgAgentMoveTo.actionID;
            ProcessMsgAgentMoveTo(NextMsg.msgAgentMoveTo);
        }

        if (NextMsg.msgAgentCancelMoveTo != null)
        {
            ProcessMsgAgentCancelMoveTo(NextMsg.msgAgentCancelMoveTo);
        }
		
		// saccFlag
        if (NextMsg.msgSaccFlag != null)
        {
            ProcessSaccFlag(NextMsg.msgSaccFlag);
        }

        // videoSync
        if (NextMsg.msgVideoSync != null)
        {
            ProcessVideoSync(NextMsg.msgVideoSync);
        }

        // MsgAnnarNetwork
        if (NextMsg.msgAnnarNetwork != null)
        {
            if (NextMsg.msgAnnarNetwork.Update == false)
            {
                ProcessMsgAnnarNetwork(NextMsg.msgAnnarNetwork);
            }
            else
            {
                ProcessMsgAnnarUpdateRates(NextMsg.msgAnnarNetwork);
            }
        }
    }

    /// <summary>
    /// Handle all received messages in asynchronous mode.
    /// </summary>
    void IncomingMessageHandlingAsyncMode()
    {

        if (MySimpleNet.MsgAvailable())
        {
            ProcessMsg(MySimpleNet.Receive());
        }
    }

    /// <summary>
    /// Handle all received messages in synchronous mode. Called in the second frame. It waits for a timeout of "SyncModeFrameTimeOut" seconds.
    /// </summary>
    void IncomingMessageHandlingSyncMode()
    {

        // Debug.Log("IncomingMessageHandlingWithSyncMode()");
        DateTime start = DateTime.Now;

        while (true)
        {

            // Process all messages: MySimplenet holds all messages from first and second frame up to this timepoint. Process them all until we get an StopSync message.
            if (MySimpleNet.MsgAvailable())
            {
                MsgObject NextMsg = MySimpleNet.Receive();

                ProcessMsg(NextMsg);

                if (NextMsg.msgStopSync != null)
                {
                    msgStartSyncAlreadySended = false;
                    Debug.Log("MsgStopSync received " + DateTime.Now.ToString());
                    return;
                }
            }
            System.Threading.Thread.Sleep(0); // sleep(0) allows a task-switch. Important: without, the unity-editor (and any other threads) freezes!

            // Timout calculation
            TimeSpan diff = DateTime.Now - start;
            // Debug.Log (diff.TotalSeconds);
            if (diff.TotalSeconds > SyncModeFrameTimeOut)
            {
                // Send a new StartSync message only if the connection still exists
                if (MySimpleNet.IsConnected)
                {
                    Debug.Log("Normal stop-sync timeout");
                    msgStartSyncAlreadySended = false; // False sends a new StartSync in the next frame
                }
                else
                {
                    // TODO - Michael: this is not working as the MySimpleNet.IsConnected return true, but the c++ was already killed with STRG+C => please fix this
                    Debug.Log("Stop-sync timeout because connection to agent-client was lost");
                    msgStartSyncAlreadySended = true;
                }

                return;
            }

        }

    }

    /// <summary>
    /// Move the agent in the world (MsgAgentMovement).
    /// </summary>
    private void ProcessMovement()
    {

        if (GetDoneDistance() < this.GoalDistance)
        {

            if (SyncMode)
            {
                CurrentMovementSpeed = MovementSpeed * SimulationTimePerFrame;
            }
            else
            {
                CurrentMovementSpeed = MovementSpeed * Time.deltaTime;
            }


            if ((GetDoneDistance() + this.CurrentMovementSpeed) > this.GoalDistance)
            {
                this.CurrentMovementSpeed = this.GoalDistance - this.GetDoneDistance();
            }

            // Remember the old position
            AgentLastPosition = transform.position;

            // Actualy move the figure and watch out for collisions
            CollisionFlags CollisionFlagTemp = MoveAgent(DirectionOfMovement, this.CurrentMovementSpeed);

            // Comment in if we need to grasp something like in the labyrinth world
            // if (CollisionFlagTemp == CollisionFlags.Sides && ControllerColliderScript.Tag != "Hand") //we wont stop, if we touch our own hand ;)

            if (CollisionFlagTemp == CollisionFlags.Sides)
            {

                if (MySimpleNet != null)
                {
                    MySimpleNet.Send(new MsgCollision() { actionID = this.MovementIDExecuting, colliderID = ControllerColliderScript.HitID });
                    MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = MovementIDExecuting, status = MsgActionExecutionStatus.Finished });
                }

                this.CurrentMovementSpeed = 0F; // Stop the moving
                this.IsCurrentMovementFinished = true; // We are done
            }
            else
            {
                // No collisions => send an acknowledge message to the agent that the movement is still under execution
                if (MySimpleNet != null)
                {
                    MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = MovementIDExecuting, status = MsgActionExecutionStatus.Walking });
                }
            }

        }
        else
        {
            // Movement is finished => send an acknowledge message to the agent
            this.CurrentMovementSpeed = 0.0F;
            if (MySimpleNet != null)
            {
                MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = MovementIDExecuting, status = MsgActionExecutionStatus.Finished });
            }
            IsCurrentMovementFinished = true;
            if (gameObject.GetComponent<Animation>()["idle"] != null)
            {
                gameObject.GetComponent<Animation>().Play("idle");
                // Debug.Log("Idle");
            }
        }
    }

    /// <summary>
    /// A simple function to execute automatically executed animations, like walk, run and idle animation. Animations belonging to certains agent messages, like grasping, 
    /// should not be executed here.
    /// </summary>
    protected virtual void PlayAnimation()
    {

        if (GetComponent<Animation>()["walk"] != null)
        {
            if (makeVideo) 
                GetComponent<Animation>()["walk"].speed = GoodWalkAnimationSpeedVideo;
            else GetComponent<Animation>()["walk"].speed = GoodWalkAnimationSpeed;
        }
        
        if (CurrentMovementSpeed > 0.01)
        {

            gameObject.GetComponent<Animation>()["walk"].wrapMode = WrapMode.Loop;
            if (!walking)
            {
                walking = true;
                if (gameObject.GetComponent<Animation>()["walk"] != null)
                    // Both options are working, use Crossfade to avoid potentiel problems with overfade 
                    // gameObject.animation.Play ("walk");
                    gameObject.GetComponent<Animation>().CrossFade("walk");
            }


        }
        else
        {

            if (walking)
            {
                walking = false;

                if (gameObject.GetComponent<Animation>()["idle"] != null)
                {
                    gameObject.GetComponent<Animation>().Play("idle");
                    // Debug.Log("Idle");
                }
                else
                {
                    // if no idle animation is available
                    if (gameObject.GetComponent<Animation>()["walk"] != null)
                    {
                        GetComponent<Animation>().clip.SampleAnimation(gameObject, 0);
                        gameObject.GetComponent<Animation>().Stop("walk");
                    }
                }
            }
            /*TODEL walking = false;
			
            if(gameObject.animation ["idle"] != null) 
                gameObject.animation.Play ("idle");
            else
            {
                //if no idle animation is available
                if(gameObject.animation ["walk"] != null) 
                {
                    gameObject.SampleAnimation(animation.clip, 0);
                    gameObject.animation.Stop("walk");
                }
            }*/
        }
    }

    /// <summary>
    /// Active in each frame during an eye saccade
    /// </summary>
    /// <param name="function">0 = linear, 1 = root, 2 = logistic</param>    
    void eyeMovement(int function)
    {
        saccTimeDone += Time.deltaTime;
        if (saccTimeDone > saccTime)
        {
            saccTimeDone = saccTime;
            saccadeActive = false;
        }

        // Rotate cameras
        if (function == 0) // Linear
        {
			Debug.Log ("Doing a linear saccade");
			cameraLeft1.transform.LookAt(LookAtTarget + (saccTimeDone / saccTime) * (newLookAtTarget - LookAtTarget));
            cameraLeft2.transform.LookAt(LookAtTarget + (saccTimeDone / saccTime) * (newLookAtTarget - LookAtTarget));
            cameraRight1.transform.LookAt(LookAtTarget + (saccTimeDone / saccTime) * (newLookAtTarget - LookAtTarget));
            cameraRight2.transform.LookAt(LookAtTarget + (saccTimeDone / saccTime) * (newLookAtTarget - LookAtTarget));
        }
        else if (function == 1) // Root
        {
            cameraLeft1.transform.LookAt(LookAtTarget + Mathf.Sqrt(saccTimeDone / saccTime) * (newLookAtTarget - LookAtTarget));
            cameraLeft2.transform.LookAt(LookAtTarget + Mathf.Sqrt(saccTimeDone / saccTime) * (newLookAtTarget - LookAtTarget));
            cameraRight1.transform.LookAt(LookAtTarget + Mathf.Sqrt(saccTimeDone / saccTime) * (newLookAtTarget - LookAtTarget));
            cameraRight2.transform.LookAt(LookAtTarget + Mathf.Sqrt(saccTimeDone / saccTime) * (newLookAtTarget - LookAtTarget));
        }
        else if (function == 2) // Logistic
        {
            cameraLeft1.transform.LookAt(LookAtTarget + (1 / (1 + Mathf.Pow((float)Math.E, -10f * ((saccTimeDone / saccTime) - 0.5f)))) * (newLookAtTarget - LookAtTarget));
            cameraLeft2.transform.LookAt(LookAtTarget + (1 / (1 + Mathf.Pow((float)Math.E, -10f * ((saccTimeDone / saccTime) - 0.5f)))) * (newLookAtTarget - LookAtTarget));
            cameraRight1.transform.LookAt(LookAtTarget + (1 / (1 + Mathf.Pow((float)Math.E, -10f * ((saccTimeDone / saccTime) - 0.5f)))) * (newLookAtTarget - LookAtTarget));
            cameraRight2.transform.LookAt(LookAtTarget + (1 / (1 + Mathf.Pow((float)Math.E, -10f * ((saccTimeDone / saccTime) - 0.5f)))) * (newLookAtTarget - LookAtTarget));
        }
        
		else if (function == 3) 
        {
			cameraLeft1.transform.LookAt(newLookAtTarget);
            cameraLeft2.transform.LookAt(newLookAtTarget);
            cameraRight1.transform.LookAt(newLookAtTarget);
            cameraRight2.transform.LookAt(newLookAtTarget);
			
			Debug.Log ("cam l:");
			Debug.Log (cameraLeft1.transform.eulerAngles);
			Debug.Log ("cam r:");
			Debug.Log (cameraRight1.transform.eulerAngles);
			
        }
			
		else if (function == 4) // Van opstal
        {
			Debug.Log ("Doing Van Opstal saccade");

			Transform EyeLf = cameraLeft1.transform;
			Transform EyeRt = cameraRight1.transform;
			
			// update saccade time
			saccTime += Time.deltaTime*Speed;
				
			// Eccentricity
			A = 1/(1-Mathf.Exp(-RR/m0));
			//Debug.Log ("A R  = " + A);
			EccR = m0*Mathf.Log(A*Mathf.Exp(vpkR*saccTime/m0)/(1+A*Mathf.Exp((vpkR*saccTime-RR)/m0)));
			A = 1/(1-Mathf.Exp(-RL/m0));
			EccL = m0*Mathf.Log(A*Mathf.Exp(vpkL*saccTime/m0)/(1+A*Mathf.Exp((vpkL*saccTime-RL)/m0)));		
			
			// Velocity
			vL = vpkL*(1-Mathf.Exp((EccL-RL)/m0));
			vR = vpkR*(1-Mathf.Exp((EccR-RR)/m0));
			
			// new position = previous Posistion + (Direction * Velocity * Timestep)
			if ((EccL > 0) && (EccR > 0))
            {
                EyeLf.rotation = Quaternion.Euler(fixL + nTargL * EccL);
                EyeRt.rotation = Quaternion.Euler(fixR + nTargR * EccR);
            }

            /*using(StreamWriter saccadeWriter = File.AppendText("ScenarioData/Vout"))	
            {	
                saccadeWriter.WriteLine(cameraLeft1.transform.rotation.eulerAngles.x+";"+cameraLeft1.transform.rotation.eulerAngles.y+";"+cameraRight1.transform.rotation.eulerAngles.x+";"+cameraRight1.transform.rotation.eulerAngles.y+";"+vL+";"+vR+";"+EccL+";"+EccR+";"+saccTimeDone);	
            }*/

            if (vL < eps && vR < eps)
            {
                saccTimeDone = saccTime;
                saccadeActive = false;
            }
        }

        if (!saccadeActive)
        {
            LookAtTarget = newLookAtTarget;
            saccTimeDone = 0f;
			
            if (MySimpleNet != null)
            {
                MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = EyeIDExecuting, status = MsgActionExecutionStatus.Finished });
            }
            Debug.Log("Saccade done.");
        }
    }



    /// <summary>
    /// Update is called once per frame.
    /// - See <A HREF="synchronDescription.pdf.">PDF file</a>.
    /// - Split up in first and second frame processing blocks
    /// - First frame sends all sensor data and the StartSync message
    /// - Second frame processes all motor data and waits for the StopSync message
    /// - Can process several messages per frame
    /// </summary>	
    protected virtual void Update()
    {
        //mibur: Click the right mouse button in the game tab (main camera) to move to this position
        //       Maybe move this somewhere else?
        if (allowClickNavigation)
        {
            // Get clicked position and move to it
            if (Input.GetMouseButtonDown(1))
            {
                Ray movePosition = Camera.main.ScreenPointToRay(Input.mousePosition);
                if (Physics.Raycast(movePosition, out var hitInfo))
                    agent.SetDestination(hitInfo.point);
            }

            // Play animation if we are walking, otherwise don't
            if (agent.pathPending || agent.remainingDistance > agent.stoppingDistance || agent.hasPath)
            {
                this.CurrentMovementSpeed = 1.0f;
                
            }
            else this.CurrentMovementSpeed = 0.0f;  
        }
        
        //If a saccade has been sent from the client: MoveEyes() -> startSaccade() -> saccadeActive = true -> Update() eyeMovement()
		if (saccadeActive) // active saccade
        {
            if (MySimpleNet != null)
            {
                MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = EyeIDExecuting, status = MsgActionExecutionStatus.InExecution });
            }
            if (flag == false)
				eyeMovement(4); //Van Opstal saccade
			
			else eyeMovement(0); //Linear saccade, see declaration of 'bool flag' for explanation
        }

        //Movement
        if (!this.IsCurrentMovementFinished)
        {
            ProcessMovement();
        }
        // Debug.Log(Time.frameCount);		

        if (MySimpleNet == null)
        {
            return;
        }

        if (ResetCalledAtStart == false)
        {
            AgentReset();
            ResetCalledAtStart = true;
        }



        bool sendingImages = false;


        switch (frameState)
        {

            // Sensor processing frame	
            case FrameState.FirstFrame:

                // Send StartSync at connection initialisation 		
                if (MySimpleNet.IsConnected &&
                    !msgStartSyncAlreadySended &&
                    SyncMode)
                {

                    msgStartSyncAlreadySended = true;
                    MySimpleNet.Send(new MsgStartSync());
                    Debug.Log("MsgStartSync sended " + DateTime.Now.ToString());
                }


                // Calibrate cameras
                cameraRight2.rect = new Rect(0.0f, 0.0f, 1f, 1f); //.rect is relative, .pixelRect is in pixel coordinates
                cameraLeft2.rect = new Rect(0.0f, 0.0f, 1f, 1f);

                // Set camera view mode
                if (camViewMode == 0) // Option 1: put cameras next to each other at upper right corner, first left then right camera
                {
                    cameraLeft1.pixelRect = new Rect(Screen.width - 2f * cameraDisplayWidth, Screen.height - 1f * cameraDisplayHeight,
                    cameraDisplayWidth, cameraDisplayHeight);
                    cameraRight1.pixelRect = new Rect(Screen.width - 1f * cameraDisplayWidth, Screen.height - 1f * cameraDisplayHeight,
                    cameraDisplayWidth, cameraDisplayHeight);
                }
                else if (camViewMode == 1) // Option 2: put cameras overlapping at upper right corner, first left then right camera
                {
                    cameraLeft1.pixelRect = new Rect(Screen.width - 1.1f * cameraDisplayWidth, Screen.height - 1.1f * cameraDisplayHeight,
                    cameraDisplayWidth, cameraDisplayHeight);
                    cameraRight1.pixelRect = new Rect(Screen.width - 1.1f * cameraDisplayWidth, Screen.height - 1.1f * cameraDisplayHeight,
                    cameraDisplayWidth, cameraDisplayHeight);
                }
                else if (camViewMode == 2) // Option 3: put cameras underneath each other (rat agent)
                {
                    cameraLeft1.pixelRect = new Rect(Screen.width - 1.0f * cameraDisplayWidth, Screen.height - 2.0f * cameraDisplayHeight,
                    cameraDisplayWidth, cameraDisplayHeight);
                    cameraRight1.pixelRect = new Rect(Screen.width - 1.0f * cameraDisplayWidth, Screen.height - 1.0f * cameraDisplayHeight,
                    cameraDisplayWidth, cameraDisplayHeight);
                }

                // Render images if needed
                if (this.TimeSinceLastImageWasSend >= this.SimulationTimePerFrame)
                {

                    RenderTexture.active = cameraRight2.GetComponent<Camera>().targetTexture;
                    cameraRight2.GetComponent<Camera>().Render();
                    RenderTexture.active = cameraLeft2.GetComponent<Camera>().targetTexture;
                    cameraLeft2.GetComponent<Camera>().Render();
					
					RenderTexture.active = MainCamera2.GetComponent<Camera>().targetTexture;
					MainCamera2.GetComponent<Camera>().Render();

                    sendingImages = true;

                }
                else
                {
                    this.TimeSinceLastImageWasSend += SyncMode ? SimulationTimePerFrame : Time.deltaTime;
                }


                // Send images
                if (sendingImages && (MySimpleNet.IsConnected))
                {
                    // Reset the counter
                    this.TimeSinceLastImageWasSend = 0F;

                    MsgImages MsgImage = new MsgImages();

                    RenderTexture.active = cameraRight2.GetComponent<Camera>().targetTexture;
                    tex_R.ReadPixels(cameraRight2.GetComponent<Camera>().pixelRect, 0, 0);
                    RenderTexture.active = cameraLeft2.GetComponent<Camera>().targetTexture;
                    tex_L.ReadPixels(cameraLeft2.GetComponent<Camera>().pixelRect, 0, 0);
					RenderTexture.active = MainCamera2.GetComponent<Camera>().targetTexture;
                    tex_M.ReadPixels(MainCamera2.GetComponent<Camera>().pixelRect, 0, 0);

                    MsgImage.leftImage = tex_L.EncodeToPNG();
                    MsgImage.rightImage = tex_R.EncodeToPNG();
					MsgImage.mainImage = tex_M.EncodeToPNG();

                    MySimpleNet.Send(MsgImage);
                }

                // Send grid position if enabled
                if (SendGridPosition)
                {
                    /// MsgGridPositionCodeLocation
                    MySimpleNet.Send(new MsgGridPosition()
                    {
                        targetX = gameObject.transform.position.x,
                        targetY = gameObject.transform.position.y,
                        targetZ = gameObject.transform.position.z,
                        targetRotationX = gameObject.transform.eulerAngles.x,
                        targetRotationY = gameObject.transform.eulerAngles.y,
                        targetRotationZ = gameObject.transform.eulerAngles.z
                    });
                }

                // Send eye information if enabled
                if (SendEyePosition)
                {
                    var curEyeRotation = cameraLeft1.transform.eulerAngles;
                    MySimpleNet.Send(new MsgEyePosition()
                    {
                        rotationPositionX = curEyeRotation.x,
                        rotationPositionY = curEyeRotation.y,
                        rotationPositionZ = curEyeRotation.z,
                        rotationVelocityX = curEyeRotation.x - lastFrameEyeRotation.x,
                        rotationVelocityY = curEyeRotation.y - lastFrameEyeRotation.y,
                        rotationVelocityZ = curEyeRotation.z - lastFrameEyeRotation.z

                    });
                    lastFrameEyeRotation = cameraLeft1.transform.eulerAngles;
                }
				
				// Send eye information if enabled
                if (SendObjectPosition)
                {
                    MySimpleNet.Send(new MsgObjectPosition()
                    {
                        greenCraneX   = GameObject.Find("carCraneGreen").transform.position.x,
						greenCraneY   = GameObject.Find("carCraneGreen").transform.position.z,
						yellowCraneX  = GameObject.Find("carCraneYellow").transform.position.x,
						yellowCraneY  = GameObject.Find("carCraneYellow").transform.position.z,
						greenRacecarX = GameObject.Find("racecar_green").transform.position.x,
						greenRacecarY = GameObject.Find("racecar_green").transform.position.z
                    });
				}

                // Send balance information if enabled
                if (SendHeadMotion)
                {
                    var curRotation = gameObject.transform.eulerAngles;
                    var curPosition = gameObject.transform.position;
                    Vector3 curVelocity = curPosition - lastFramePosition;
                    Vector3 curRotationVelocity = curRotation - lastFrameRotation;
                    MySimpleNet.Send(new MsgHeadMotion()
                    {
                        velocityX = curVelocity.x,
                        velocityY = curVelocity.y,
                        velocityZ = curVelocity.z,
                        accelerationX = curVelocity.x - lastFrameVelocity.x,
                        accelerationY = curVelocity.y - lastFrameVelocity.y,
                        accelerationZ = curVelocity.z - lastFrameVelocity.z,
                        rotationVelocityX = curRotation.x - lastFrameRotation.x,
                        rotationVelocityY = curRotation.y - lastFrameRotation.y,
                        rotationVelocityZ = curRotation.z - lastFrameRotation.z,
                        rotationAccelerationX = curRotationVelocity.x - lastFrameRotationVelocity.x,
                        rotationAccelerationY = curRotationVelocity.y - lastFrameRotationVelocity.y,
                        rotationAccelerationZ = curRotationVelocity.z - lastFrameRotationVelocity.z
                    });
                    lastFrameRotation = gameObject.transform.eulerAngles;
                    lastFramePosition = gameObject.transform.position;
                    lastFrameVelocity = curVelocity;
                    lastFrameRotationVelocity = curRotationVelocity;

                }

                frameState = FrameState.SecondFrame;
                break;


            // Motor processing frame	
            case FrameState.SecondFrame:

                // Message Handling
                if (MySimpleNet.IsConnected)
                {

                    if (SyncMode == true)
                    {
                        IncomingMessageHandlingSyncMode();
                    }
                    else
                    {
                        IncomingMessageHandlingAsyncMode();
                    }
	 
					// Eyemovement
                    if (EyeMovementInLookAtMode && !saccadeActive)
                    {
						// In LookAtMode we always redirect the cameras to the point of interest
                        cameraLeft1.transform.LookAt(LookAtTarget);
                        cameraRight1.transform.LookAt(LookAtTarget);
                        cameraLeft2.transform.LookAt(LookAtTarget);
                        cameraRight2.transform.LookAt(LookAtTarget);

                        if ((cameraLeft1.transform.localEulerAngles.y > 130.0f) && (cameraLeft1.transform.localEulerAngles.y < 230.0f)) // Eye rotation outside accepted range
                        {
                            EyeMovementInLookAtMode = false;
                            Debug.Log("LookAtTarget outside the accepted angle (+- 130)");
                            if (MySimpleNet != null)
                            {
                                MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = EyeIDExecuting, status = MsgActionExecutionStatus.Aborted });
                            }
                        }
                    } 
                    else if (!saccadeActive)
                    {
                        
						// Always redirect the cameras relative to the agentrotation (not head)
                        cameraLeft1.transform.rotation = gameObject.transform.rotation * Quaternion.AngleAxis(panLeft, Vector3.up) * Quaternion.AngleAxis(tilt, Vector3.left);
                        cameraRight1.transform.rotation = gameObject.transform.rotation * Quaternion.AngleAxis(panRight, Vector3.up) * Quaternion.AngleAxis(tilt, Vector3.left);
                        cameraLeft2.transform.rotation = gameObject.transform.rotation * Quaternion.AngleAxis(panLeft, Vector3.up) * Quaternion.AngleAxis(tilt, Vector3.left);
                        cameraRight2.transform.rotation = gameObject.transform.rotation * Quaternion.AngleAxis(panRight, Vector3.up) * Quaternion.AngleAxis(tilt, Vector3.left);

                        headLookScript.target = LookAtTarget = standardLookAtPoint.transform.position;
                        
                    }
                }


                // Movement
                if (!this.IsCurrentMovementFinished)
                {
                    ProcessMovement();
                }

                // Animations

                PlayAnimation();
                TestGraspAnimations();
                GraspActionExecutionMessageSending();

                frameState = FrameState.FirstFrame;
                break;

        }
    }

    /// <summary>
    /// Gets the last arm message.
    /// used by handHollider.cs
    /// </summary>
    public ArmMsg getLastArmMsg()
    {
        return lastArmMsg;
    }

    /// <summary>
    /// Gets the righthand.
    /// </summary>
    public GameObject getRighthand()
    {
        return this.rightHand;
    }

    /// <summary>
    /// Sets the righthand.
    /// </summary>
    public void setRighthand(GameObject rightHand)
    {
        this.rightHand = rightHand;
    }

    /// <summary>
    /// Gets the right grasped object.
    /// </summary>
    public GameObject getRightGraspedObject()
    {
        return this.rightGraspedObject;
    }

    /// <summary>
    /// Sets the right grasped object.
    /// </summary>
    public void setRightGraspedObject(GameObject rightGraspedObject)
    {
        this.rightGraspedObject = rightGraspedObject;
    }

    /// <summary>
    /// Sets the displayCameraVR and enable/disable cameras
    /// </summary>
    public void setDisplayCameraVR(bool displayCameraVR)
    {
        this.displayCameraVR = displayCameraVR;
        cameraLeft1.enabled = displayCameraVR;
        cameraRight1.enabled = displayCameraVR;

    }




    #region Grasping animations

    /// <summary>
    /// Behavior function for MsgAgentGraspID. This is an example implementation and could be overridden in a derived class.
    /// </summary>
    /// <param name="msg">MsgAgentGraspID object</param>    
    protected virtual void ProcessMsgAgentGraspID(MsgAgentGraspID msg)
    {
        /* Debug.Log (String.Format ("AgentGraspID received ({0:d})",
                        msg.objectID));
         * 
         */

        // Sending ObejctID which belong to object which will grasp.
        int objectID = msg.objectID;

        // Init to targetName firstValue in order to avoid a error
        string targetName = "";

        // Assign objectName according to receiving value
        switch (objectID)
        {
            case 1: targetName = "Grasp1";
                break;
            case 2: targetName = "Grasp2";
                break;
            case 3: targetName = "Grasp3";
                break;
            default:
                break;
        }
        // Receiving valuable is finding.
        GameObject P = GameObject.Find(targetName.ToString());

        // Object Name
        // Debug.Log("Grasp object " + P.name + " via Protobuf-ObjectID=" + msg.objectID);


        if (P != null && !interpolateAnimations.animate(P.transform.position.x, P.transform.position.y, P.transform.position.z))
        {
            Debug.Log("Object with ID " + objectID + " at position (" + P.transform.position + ") is not in range of the arm, hence it is not graspable");
            if (MySimpleNet != null)
            {
                MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = ArmIDExecuting, status = MsgActionExecutionStatus.Aborted });
            }
        }
    }

    /// <summary>
    /// Behavior function for MsgAgentGraspPos.  Processes the message agent grasp position, hence grasp an object at a certain position in the field of view.
    /// </summary>
    protected virtual void ProcessMsgAgentGraspPos(MsgAgentGraspPos msg)
    {
        //Debug.Log (String.Format ("AgentGraspPos received ({0:f},{1:f})",  msg.targetX,  msg.targetY));

        // Receiving from client.target x
        float x1 = msg.targetX;
        // Receiving from client.target y
        float y1 = msg.targetY;



        Vector3 graspPoint = new Vector3();
        int ret = transformEyeToGlobalCoordinates(x1, y1, ref graspPoint);
        if (ret == 0)
        {
            if (!interpolateAnimations.animate(graspPoint.x, graspPoint.y, graspPoint.z))
            {
                Debug.Log("Object at " + graspPoint + " for target position (" + x1 + "," + y1 + ") is not in range of the arm, hence it is not graspable");
                if (MySimpleNet != null)
                {
                    MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = ArmIDExecuting, status = MsgActionExecutionStatus.Aborted });
                }
            }
            // InitializeGraspActionExecutionMessageSending();
        }
        else
        {
            if (MySimpleNet != null)
            {
                MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = ArmIDExecuting, status = MsgActionExecutionStatus.Aborted });
            }
        }
    }

    /// <summary>
    /// Processes the message grasp release (exemplary implementation).
    /// </summary>
    protected virtual void ProcessMsgGraspRelease(MsgAgentGraspRelease msg)
    {
        if (MySimpleNet != null)
        {
            MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = ArmIDExecuting, status = MsgActionExecutionStatus.InExecution });
        }

        if (rightGraspedObject != null)
        {
            // Change parent to global one, this releases the object
            rightGraspedObject.transform.parent = null;
            rightGraspedObject.GetComponent<Rigidbody>().useGravity = true;   // Enable gravity
            rightGraspedObject.GetComponent<Rigidbody>().isKinematic = false; // Enable pyhsics

            // Enable all collider in the grasped object again
            Collider col = rightGraspedObject.GetComponent<Collider>();
            if (col != null)
                col.enabled = true;
            foreach (Transform child in rightGraspedObject.transform)
            {
                col = child.GetComponent<Collider>();
                if (col != null)
                    col.enabled = true;
            }

            // Mark object as released
            rightGraspedObject = null;
            lastArmMsg = ArmMsg.ArmMsgNone;

            // Send success to agent
            if (MySimpleNet != null)
            {
                MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = msg.actionID, status = MsgActionExecutionStatus.Finished });
            }
        }
        else
        {
            //Send failure to agent
            if (MySimpleNet != null)
            {
                MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = msg.actionID, status = MsgActionExecutionStatus.Aborted });
            }
        }
    }

    /// <summary>
    /// Processes the message agent turn (works with coroutine)
    /// </summary>
    protected virtual void ProcessMsgAgentTurn(MsgAgentTurn msg)
    {
        IsCurrentMovementFinished = false;
        if (MySimpleNet != null)
        {
            MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = msg.actionID, status = MsgActionExecutionStatus.Rotating });
        }

        StartCoroutine(DoRotation(msg.degree, msg));
    }
	
	/// <summary>
    /// saccFlag
    /// </summary>
    protected virtual void ProcessSaccFlag(MsgSaccFlag msg)
    {
		if (msg.i == 1)
			flag = true;
    }

    /// <summary>
    /// videoSync
    /// </summary>
    protected virtual void ProcessVideoSync(MsgVideoSync msg)
    {
		if (msg.i == 1)
            syncContinue = true;
    }

    /// <summary>
    /// Turns the agent without a message (works with coroutine)
    /// </summary>
    protected virtual void ProcessAgentTurn(float degree)
    {
        IsCurrentMovementFinished = false;

        StartCoroutine(DoRotation(degree));
    }

    /// <summary>
    /// Processes the message agent move to (pathwalking)
    /// </summary>
    protected virtual void ProcessMsgAgentMoveTo(MsgAgentMoveTo msg)
    {
        // for overloading
    }

    /// <summary>
    /// Processes the message agent cancel move to (stops pathwalking)
    /// </summary>
    protected virtual void ProcessMsgAgentCancelMoveTo(MsgAgentCancelMoveTo msg)
    {
        // for overloading
    }

    /// <summary>
    /// Coroutine for MsgAgentTurn
    /// </summary>
    protected IEnumerator DoRotation(float degree, MsgAgentTurn msg = null)
    {
        //MB: make sure to always performs the shorter turn
		if (degree > 180)	
			degree = (360 - degree) * -1;
		if (degree < -180)
			degree = (360 + degree);
		
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
        while (donePercent < 0.2f)
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
        while (donePercent < 0.8f)
        {
            rot = maxSpeed * Time.deltaTime;
            t.Rotate(0.0f, sgn * rot, 0.0f);  
			done += rot;
            donePercent = done / total;
            yield return null;
        }

        // From 80% to 100% accelerate negative linear
        while (donePercent < 1.0f)
        {
            speedFactor = n2 - m * donePercent;
            rot = speedFactor * maxSpeed * Time.deltaTime;
            t.Rotate(0.0f, sgn * rot, 0.0f);      
			done += rot;
            donePercent = done / total;
            yield return null;
        }

        // Set the rotation angles to desired value
        t.eulerAngles = startRot + new Vector3(0.0f, degree, 0.0f);

        IsCurrentMovementFinished = true;

        if (msg != null && MySimpleNet != null)
        {
            MySimpleNet.Send(new MsgActionExecutionStatus() { actionID = msg.actionID, status = MsgActionExecutionStatus.Finished });
        }
    }

    /// <summary>
    /// Transforms x/y coordinates in retina-coordinate system to global one, hence at which position the eye is looking.
    /// Details:
    /// - Eye-coordinates are in the left camera in camera resolution and 0/0 is left upper corner.
    /// - We search the point in the scene which is projecting at the given retina coordinates.
    /// - We send out a ray from the left eye to a virtual point on a plane in the front of the eye.
    /// - This ray hits the first target with attached colliders.
    /// - We return this position in global coordinates.
    /// </summary>
    /// <param name='Filename'>
    /// The global position.
    /// </param>
    /// <returns>
    /// -1 if x1,y1 are outside the camera resolution, -2 if no point could be found, -3 if it has no rigidbody or -4 if it is not graspable, 0 if a point was succesfully calculated
    /// </returns>
    int transformEyeToGlobalCoordinates(float x1, float y1, ref Vector3 globalPos)
    {
        // Variable depth for virtual plane (doesn't matter)
        float d = 2;

        // Check if it is inside camera resolution
        if (x1 > ImageResolutionWidth || y1 > ImageResolutionHeight)
        {
            Debug.Log("transformEyeToGlobalCoordinates(): Specifiy target outside the camera resolution");
            return -1;
        }
        else
        {
            // Shift coordinates to middle point of left image
            x1 = x1 - ImageResolutionWidth / 2;
            y1 = -(y1 - ImageResolutionHeight / 2); // Minus because the y-axis is inverted: The agent side has 0/0 at the upper left corner whereby the here used virtual plane 
            // (and the cameras) has 0/0 at lower left corner

            // Calculate virtual target point at depth d in a virtual plane.

            // a2 = tan(gamma/2)*d
            float a2 = Mathf.Tan((FovHorizontal / 2) / 180 * Mathf.PI) * d;    // Resolution in global units in x-adirection of the plane/2
            float b2 = Mathf.Tan((FovVertical / 2) / 180 * Mathf.PI) * d;      // In y-direction
            float x2 = x1 / (ImageResolutionWidth / 2) * a2;                     // x1 in the coordinate system of the plane, whereby 0 is the middle
            float y2 = y1 / (ImageResolutionHeight / 2) * b2;                    // y1

            // Create vector for raycast end position
            // - we have to use a point further away from the viewplane, this is determined by d
            // - we use camera.transform to map the local camera coordinate system to the global coordinate system used for grasping
            Vector3 vec = cameraLeft2.transform.rotation * (new Vector3(x2, y2, d));

            // DEBUG
            // Debug.Log("X1="+x1+", X2="+x2+ ", A2="+a2+", B2="+b2);
            // Debug.Log("CameraL2= " + cameraLeft2.transform.position + ", "+cameraLeft2.transform.rotation+", Vec= " + vec); 		

            // Check for raycast by drawing line from left camera (need an empty object 'forLine' with an lineRenderer)
            // Important: we destroy the object ONLY if we successfully grasp the object (case: animation was finished, or case animation was aborted due to second grasping) or for security here 
            // If the grasping is otherwise failing (not in range, not usable, etc), we doesn't destroy it for simplicity of the implementation
            if (debugLine != null)
                Destroy(debugLine);
            debugLine = Instantiate(Resources.Load("forLine") as UnityEngine.Object, new Vector3(0, 0, 0), Quaternion.identity) as GameObject;
            debugLine.GetComponent<LineRenderer>().SetPosition(0, cameraLeft2.transform.position + vec * 0.1f);
            debugLine.GetComponent<LineRenderer>().SetPosition(1, cameraLeft2.transform.position + vec);

            // Value for keeping the crashed object
            RaycastHit hit;

            // Check if it crashed until distance of 100 units
            if (Physics.Raycast(cameraLeft2.transform.position, vec, out hit))
            {

                if (hit.rigidbody == null)
                {
                    Debug.Log("Found object '" + hit.transform.name + "' at target coordinates (" + x1 + "," + y1 + "), but it has no rigidbody.");
                    return -3;
                }

                if (hit.rigidbody.tag != "usable")
                {
                    Debug.Log("Found object '" + hit.transform.name + "' at target coordinates (" + x1 + "," + y1 + "), but it is not usable.");
                    return -4;
                }

                Debug.Log("Found object '" + hit.transform.name + "' on ray at point " + hit.point); //DEBUG

                globalPos = hit.point;
                return 0;
            }
            else
            {
                Debug.Log("No object found target position (" + x1 + "," + y1 + ")");
                return -2;
            }
        }
    }

    #endregion
}
