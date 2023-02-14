/**
@brief Control class for free movable camera

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using UnityEngine;

public class FreeMovingCamera : MonoBehaviour
{
    private Vector3 startingPos;
    private Quaternion startingRot;
    public float speed = 1.0f;
    public float rotationSpeed = 50000.0f;
    public float anglePerFrame = 1.0f;

    void Start () {
        startingPos = transform.position;
        startingRot = transform.rotation;
    }

	void Update () {
        if (Input.GetKey(KeyCode.Q))
            transform.Rotate(Vector3.up, -anglePerFrame, Space.World);

        if (Input.GetKey(KeyCode.E))
            transform.Rotate(Vector3.up, anglePerFrame, Space.World);

        if (Input.GetKey(KeyCode.R))
            transform.Rotate(Vector3.right, -anglePerFrame, Space.Self);

        if (Input.GetKey(KeyCode.F))
            transform.Rotate(Vector3.right, anglePerFrame, Space.Self);

        if (Input.GetKey(KeyCode.W) || Input.GetKey(KeyCode.UpArrow))
            transform.Translate(Vector3.forward * speed, Space.Self);

        if (Input.GetKey(KeyCode.S) || Input.GetKey(KeyCode.DownArrow))
            transform.Translate(Vector3.forward * -speed, Space.Self);

        if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow))
            transform.Translate(Vector3.right * -speed, Space.Self);

        if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow))
            transform.Translate(Vector3.right * speed, Space.Self);

        if (Input.GetKeyDown(KeyCode.Z)) {
            transform.position = startingPos;
            transform.rotation = startingRot;
        }

    }
}
