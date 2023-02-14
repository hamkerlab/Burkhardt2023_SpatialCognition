Shader "CylindricProjection" {
	Properties {
		_FoVV ("Vertical Field of View", Float) = 60.0
		_F ("Far Sphere", Float) = 100.0
		_N ("Near Sphere", Float) = 0.3
		_Aspect("Angle Aspect", Float) = 1.77778
		_YValue("Y-Value", Float) = 0.5
	}
	SubShader {
		Pass{

			CGPROGRAM
			// Upgrade NOTE: excluded shader from OpenGL ES 2.0 because it does not contain a surface program or both vertex and fragment programs.
			#pragma exclude_renderers gles

			#pragma vertex vert
			#include "UnityCG.cginc"

			struct v2f {
				float4 pos : POSITION;
			};

			float _F;
			float _N;
			float _FoVV;
			float _Aspect;
			float _YValue;

			v2f vert(appdata_base v)
			{
				v2f o;
				const float PI = 3.14159;
				float phi = _FoVV * PI / 360.0f;
				float theta = phi * _Aspect;

				o.pos = mul(UNITY_MATRIX_MV, v.vertex);

				float d = length(o.pos.xz);

				o.pos.xy /= d;

				float alpha = asin(o.pos.x);
				o.pos.x = alpha / theta;

				//float volumeHeight = abs(o.pos.z) * tan(phi) / d;

				//float volumeHeight = tan(phi);				// mid point
				float volumeHeight = tan(phi) * cos(theta * _YValue);
				o.pos.y /= -volumeHeight;
			
				o.pos.z = -sign(o.pos.z) * (d - _N) / (_F - _N);
				
				o.pos.w = 1.0f;	
				
				return o;
			}

			ENDCG
		}
	} 
	Fallback "Diffuse"
}
