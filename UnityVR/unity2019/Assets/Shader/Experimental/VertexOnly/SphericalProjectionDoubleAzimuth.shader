Shader "SphericalProjectionDA" {
	Properties {
		_FoVV ("Vertical Field of View", Float) = 60.0
		_F ("Far Sphere", Float) = 100.0
		_N ("Near Sphere", Float) = 0.3
		_Aspect("Angle Aspect", Float) = 1.52488
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

			v2f vert(appdata_base v)
			{
				v2f o;
				const float PI = 3.14159;
				float phi = _FoVV * PI / 360.0f;
				float theta = phi * _Aspect;

				o.pos = mul(UNITY_MATRIX_MV, v.vertex);

				float d = length(o.pos.xyz);
				//float yp = asin(o.pos.y / d);
				//theta /= cos(yp);
				//o.pos.x = asin(o.pos.x / (cos(yp) * d)) / theta;
				float alpha = asin(o.pos.x / d);
				float beta = asin(o.pos.y / d);

				float azPrim = asin(o.pos.y / (cos(alpha) * d));
				float azSec = asin(o.pos.x / (cos(beta) * d));

				//o.pos.x = sin(azSec) / sin(theta);

				//o.pos.y = -sin(azPrim) / sin(phi);

				//theta /= cos(beta);
				//phi /= cos(alpha);

				o.pos.x = azSec / theta;

				o.pos.y = -azPrim / phi;
				
			
				o.pos.z = -sign(o.pos.z) * (d - _N) / (_F - _N);
				
				o.pos.w = 1.0f;	
				
				return o;
			}

			ENDCG
		}
	} 
	Fallback "Diffuse"
}
