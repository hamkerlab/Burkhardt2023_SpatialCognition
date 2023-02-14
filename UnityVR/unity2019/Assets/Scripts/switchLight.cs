/**
@brief Script for a which turns out a lightswitch on collision

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using System.Collections;
using UnityEngine;

public class switchLight : MonoBehaviour
{
    #region Fields

	/// <summary>
    /// Light object which the script should control
    /// </summary>
    public Light linkedLight;

    #endregion Fields

    #region Methods

    void OnControllerColliderHit(ControllerColliderHit hit)
    {
        if (hit.gameObject.tag == "LightSwitch")
            linkedLight.enabled = !linkedLight.enabled;
    }

    void Start()
    {
    }

    void Update()
    {
    }

    #endregion Methods
}
