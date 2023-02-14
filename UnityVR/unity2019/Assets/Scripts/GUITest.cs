/**
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using UnityEngine;
using System.Collections;

public class GUITest : MonoBehaviour {
            
    void OnGUI(){
        GUI.Box (new Rect (0,0,100,50), "Top-left");
        GUI.Box (new Rect (Screen.width - 100,0,100,50), "Top-right");
        GUI.Box (new Rect (0,Screen.height - 50,100,50), "Bottom-left");
        GUI.Box (new Rect (Screen.width - 100,Screen.height - 50,100,50), "Bottom-right");
    }

}