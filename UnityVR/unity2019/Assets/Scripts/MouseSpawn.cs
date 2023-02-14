/**
@brief Sample script for spawning an object at mouse position

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/

using System.Collections;
using UnityEngine;

public class MouseSpawn : MonoBehaviour
{
    #region Fields

    public Transform prefabKey1;
    public Transform prefabKey2;
    public Transform prefabKey3;

    #endregion Fields

    #region Methods

    // Use this for initialization
    void Start()
    {
    }

    // Update is called once per frame
    void Update()
    {
        //x-Koordinate der Maus wird in Variable mousex geschrieben
        float mousex = Input.mousePosition.x;
        //y-Koordinate der maus wird in Variable mousey geschrieben
        float mousey = Input.mousePosition.y;
        //die Positin zum spawnen des Blocks wird in die Variable ray geschrieben
        Ray ray = Camera.main.ScreenPointToRay (new Vector3 (mousex, mousey, 0));
        //?
        RaycastHit hit;
        //?
        Debug.DrawRay(ray.origin, ray.direction*10, Color.cyan, 10000);
        if (Physics.Raycast (ray, out hit, 200)) {

        }
        //wenn Taste 1 gedrückt wird
        if (Input.GetKeyDown ("1")) {
            //spawne den ersten block ander oben ausgerechneten Position
            Instantiate (prefabKey1, hit.point, Quaternion.identity);

        }
        //wenn Taste 2 gedrückt wird
        if (Input.GetKeyDown ("2")) {
            //spawne den zweiten block ander oben ausgerechneten Position
            Instantiate (prefabKey2, hit.point, Quaternion.identity);

        }
        //wenn Taste 3 gedrückt wird
        if (Input.GetKeyDown ("3")) {
            //spawne den dritten block ander oben ausgerechneten Position
            Instantiate (prefabKey3, hit.point, Quaternion.identity);

        }
        //wenn Taste c gedrückt wird
        if (Input.GetKeyDown ("c")) {
            //lösche alle Objekte mit dem tag turm
            Destroy (GameObject.FindWithTag ("bauturm"));
        }
    }

    #endregion Methods
}