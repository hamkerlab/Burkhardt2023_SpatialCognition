// Upgrade NOTE: replaced '_Object2World' with 'unity_ObjectToWorld'

Shader "SphericalProjectionLit" {
	// lighting is simple diffuse for multiple light sources
	// no shadows are received from other objects
Properties {
	_Color("Main Color", Color) = (1,1,1,1)
	_MainTex("Base (RGB)", 2D) = "white" {}
	// following properties are set via script depending on the camera
	_FoVV("Vertical Field of View", Float) = 60.0
	_F("Far Sphere", Float) = 100.0
	_N("Near Sphere", Float) = 0.3
	_Aspect("Image Aspect", Float) = 1.77778
}
CGINCLUDE
#include "UnityCG.cginc"
#include "Lighting.cginc"
#include "AutoLight.cginc"
ENDCG

SubShader{
		Tags{ "RenderType" = "Opaque"}
		LOD 200
		Cull off

	Pass{
		Tags{ "LightMode" = "ForwardBase" }
		CGPROGRAM
			#pragma vertex vert
			#pragma fragment frag
			#pragma multi_compile_fwdbase
				

			struct v2f {
				float4 pos : SV_POSITION;
				float2 uv : TEXCOORD0;
				float3 worldPos: TEXCOORD1;
				float3 n : TEXCOORD2;
				LIGHTING_COORDS(3,4)
			};

			float _F;
			float _N;
			float _FoVV;
			float _Aspect;

			float4 _MainTex_ST;
			sampler2D _MainTex;
			fixed4 _Color;

			// custom vertex shader
			v2f vert(appdata_base v)
			{
				v2f o;
				const float PI = 3.14159;

				// the standard Model-View-Transformation
				o.pos = mul(UNITY_MATRIX_MV, v.vertex);

				// here calculations for custom projection begin
				float PHI = _FoVV * PI / 360.0f;
				float THETA = PHI * _Aspect;

				float d = length(o.pos.xyz);
				float polar = asin(o.pos.y / d);
				float cp = cos(polar);

				o.pos.x = asin(o.pos.x / (cp * d)) * cp / THETA;
				o.pos.y = -polar / PHI;
				
				float z =  (d - _N) / (_F - _N);
				z = 1.0f - z;

				if (z <= 0.0f)
				{
					o.pos.z = -0.0001f;
				}
				else 
				{
					o.pos.z = -sign(o.pos.z) * z;
				}

				o.pos.w = 1.0f;

				// here vertex properties for texturing and lighting
					// are transformed to fragment shader
				o.uv = TRANSFORM_TEX(v.texcoord, _MainTex);
				o.worldPos = mul(unity_ObjectToWorld, v.vertex).xyz;
				o.n = normalize(mul((float3x3)unity_ObjectToWorld, v.normal));

				TRANSFER_VERTEX_TO_FRAGMENT(o);

				return o;
			}

			// simple per-pixel diffuse and ambient lighting
			fixed4 frag (v2f i) : COLOR // SV_Target in Unity 5
			{
				fixed4 col = tex2D(_MainTex, i.uv) * _Color;

				half nl;
				// w-compontn == 0 means directional light
				// != 0 means point/spot-light
				if (_WorldSpaceLightPos0.w == 0.0)
					nl = max(0.0f, dot(i.n, normalize(_WorldSpaceLightPos0.xyz)));
				else
				{
					float3 vertexToLight = _WorldSpaceLightPos0.xyz - i.worldPos.xyz;
					nl = max(0.0f, dot(i.n, normalize(vertexToLight)));
				}

				half att = LIGHT_ATTENUATION(i);

				float3 ambient = UNITY_LIGHTMODEL_AMBIENT.rgb * _Color.rgb;
				float3 diffuse = nl * _LightColor0.rgb * _Color.rgb * att;

				col *= float4 ((diffuse + ambient) * 2.0f, 1.0f);

				return col;
			}

		ENDCG
	}
	// here follows the same code as above for additional passes
				// for multiple light sources
	Pass{
		Tags{ "LightMode" = "ForwardAdd" }
		Blend One One
		CGPROGRAM
			#pragma vertex vert
			#pragma fragment frag
			#pragma multi_compile_fwdadd


			struct v2f {
				float4 pos : SV_POSITION;
				float2 uv : TEXCOORD0;
				float3 worldPos: TEXCOORD1;
				float3 n : TEXCOORD2;
				LIGHTING_COORDS(3, 4)
			};

			float _F;
			float _N;
			float _FoVV;
			float _Aspect;

			float4 _MainTex_ST;
			sampler2D _MainTex;
			fixed4 _Color;

			v2f vert(appdata_base v)
			{
				v2f o;
				const float PI = 3.14159;
				float PHI = _FoVV * PI / 360.0f;
				float THETA = PHI * _Aspect;

				o.pos = mul(UNITY_MATRIX_MV, v.vertex);

				float d = length(o.pos.xyz);
				float polar = asin(o.pos.y / d);
				float cp = cos(polar);

				o.pos.x = asin(o.pos.x / (cp * d)) * cp / THETA;
				o.pos.y = -polar / PHI;
				
				float z =  (d - _N) / (_F - _N);
				z = 1.0f - z;

				if (z <= 0.0f)
				{
					o.pos.z = -0.0001f;
				}
				else 
				{
					o.pos.z = -sign(o.pos.z) * z;
				}

				o.pos.w = 1.0f;

				o.uv = TRANSFORM_TEX(v.texcoord, _MainTex);
				o.worldPos = mul(unity_ObjectToWorld, v.vertex).xyz;
				o.n = normalize(mul((float3x3)unity_ObjectToWorld, v.normal));

				TRANSFER_VERTEX_TO_FRAGMENT(o);

				return o;
			}

			fixed4 frag(v2f i) : COLOR
			{
				fixed4 col = tex2D(_MainTex, i.uv) * _Color;

				half nl;
				if (_WorldSpaceLightPos0.w == 0.0)
					nl = max(0.0f, dot(i.n, normalize(_WorldSpaceLightPos0.xyz)));
				else
				{
					float3 vertexToLight = _WorldSpaceLightPos0.xyz - i.worldPos.xyz;
					nl = max(0.0f, dot(i.n, normalize(vertexToLight)));
				}

				half att = LIGHT_ATTENUATION(i);

				float3 diffuse = nl * _LightColor0.rgb * _Color.rgb * att;

				col *= float4 (diffuse * 1.0f, 1.0f);

				return col;
			}

		ENDCG
	}
} 
Fallback "Diffuse"
}
