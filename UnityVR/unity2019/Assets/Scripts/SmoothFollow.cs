/**
@brief Script for a 3rd Person camera

@details Attachted to an 3D object in the scene, a camera specified in the member variable "target" get fixed to that object.

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using System.Collections;
using UnityEngine;

// Place the script in the Camera-Control group in the component menu
[AddComponentMenu("Camera-Control/Smooth Follow")]
public class SmoothFollow : MonoBehaviour
{
    #region Fields

    // The distance in the x-z plane to the target
    public float distance = 5f;

    // the height we want the camera to be above the target
    public float height = 5.0f;

    // How much we
    public float heightDamping = 2.0f;
    public float rotationDamping = 3.0f;

    // The target we are following
    public Transform target;

    #endregion Fields

    #region Methods

    void LateUpdate()
    {
        // Early out if we don't have a target
        if (!target)
            return;

        // Calculate the current rotation angles
        float wantedRotationAngle = target.eulerAngles.y;
        float wantedHeight = target.position.y + height;

        float currentRotationAngle = transform.eulerAngles.y;
        float currentHeight = transform.position.y;

        // Damp the rotation around the y-axis
        currentRotationAngle = Mathf.LerpAngle (currentRotationAngle, wantedRotationAngle, rotationDamping);

        // Damp the height
        currentHeight = Mathf.Lerp (currentHeight, wantedHeight, heightDamping * Time.deltaTime);

        // Convert the angle into a rotation
        Quaternion currentRotation = Quaternion.Euler (0, currentRotationAngle, 0);

        // Set the position of the camera on the x-z plane to:
        // distance meters behind the target
        transform.position = target.position;
        transform.position -= currentRotation * Vector3.forward * distance;

        // Set the height of the camera
        transform.position = new Vector3(transform.position.x,  currentHeight, transform.position.z);

        // Always look at the target
        transform.LookAt (target);
    }

    // Use this for initialization
    void Start()
    {
    }

    // Update is called once per frame
    void Update()
    {
    }

    #endregion Methods
}