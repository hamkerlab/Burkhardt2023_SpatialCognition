// Upgrade NOTE: replaced '_Object2World' with 'unity_ObjectToWorld'

// See SphericalProjectionLit.shader for comments and comparison
Shader "SphericalProjectionDPLit" {
	Properties {
		_Color("Main Color", Color) = (1,1,1,1)
		_MainTex("Base (RGB)", 2D) = "white" {}
		_FoVV ("Vertical Field of View", Float) = 60.0
		_F ("Far Sphere", Float) = 100.0
		_N ("Near Sphere", Float) = 0.3
		_Aspect("Angle Aspect", Float) = 1.52488
	}
CGINCLUDE
#include "UnityCG.cginc"
#include "Lighting.cginc"
#include "AutoLight.cginc"
ENDCG
	SubShader {
			Tags{ "RenderType" = "Opaque" }
			LOD 200
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

			v2f vert(appdata_base v)
			{
				v2f o;
				const float PI = 3.14159;
				float PHI = _FoVV * PI / 360.0f;
				float THETA = PHI * _Aspect;

				o.pos = mul(UNITY_MATRIX_MV, v.vertex);

				float d = length(o.pos.xyz);

				float alpha = asin(o.pos.x / d);
				float beta = asin(o.pos.y / d);

				o.pos.x = alpha / THETA;

				o.pos.y = -beta / PHI;
			
				float z = (d - _N) / (_F - _N);

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
				o.n = mul((float3x3)unity_ObjectToWorld, SCALED_NORMAL);

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

				float3 ambient = UNITY_LIGHTMODEL_AMBIENT.rgb * _Color.rgb;
				float3 diffuse = nl * _LightColor0.rgb * _Color.rgb * att;

				col *= float4 ((diffuse + ambient) * 2.0f, 1.0f);

				return col;
			}

			ENDCG
		}
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

				float alpha = asin(o.pos.x / d);
				float beta = asin(o.pos.y / d);

				o.pos.x = alpha / THETA;

				o.pos.y = -beta / PHI;

				float z = (d - _N) / (_F - _N);

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
				o.n = mul((float3x3)unity_ObjectToWorld, SCALED_NORMAL);

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

				col *= float4 (diffuse * 2.0f, 1.0f);

				return col;
			}

			ENDCG
		}
	} 
	Fallback "Diffuse"
}
