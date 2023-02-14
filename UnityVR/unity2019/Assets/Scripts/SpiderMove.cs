/**
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using UnityEngine;
using System.Collections;

public class SpiderMove : MonoBehaviour {
	public Vector3 B;
	IEnumerator Start () {
		Vector3 A = this.transform.position;
		while (true) {
			yield return StartCoroutine(MoveObject(transform, A, B, 6.0f));
			yield return StartCoroutine(MoveObject(transform, B, A, 6.0f));
		}
	}
	
	// Update is called once per frame
	IEnumerator MoveObject(Transform thisTransform, Vector3 startPos, Vector3 endPos, float time)
	{
		var i= 0.0f;
		var rate= 1.0f/time;
		while (i < 1.0f) {
			i += Time.deltaTime * rate;
			thisTransform.position = Vector3.Lerp(startPos, endPos, i);
			yield return null; 
		}
	}
}
