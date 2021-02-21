#include <iostream>
#include <cmath>

using namespace std;

class PrimalityTests{
    public:
        bool is_prime(long n){
            if (!is_sprp(n)){
                return false;
            };
            int a = 5;
            int s = 2;
            while (legendre(a, n) != n-1) {
                int s = -s;
                int a = s-a;
            }
            return is_lucas_prp(n, a);
        }
    private:
        bool is_lucas_prp(long n, int D){
            int P = 1;
            int Q = (1-D) >> 2;

            // n+1 = 2**r*s where s is odd
            int s = n+1;
            int r = 0;
            while ((s & 1) == 0) {
                r += 1;
                s >>= 1;
            }
            // calculate the bit reversal of (odd) s
            // e.g. 19 (10011) <=> 25 (11001)
            int t = 0;
            while(s > 0) {
                if (s & 1){
                    t += 1;
                    s -= 1;
                }
                else{
                    t <<= 1;
                    s >>= 1;
                }
            }
            // use the same bit reversal process to calculate the sth Lucas number
            // keep track of q = Q**n as we go
            int U = 0;
            int V = 2;
            int q = 1;
            // mod_inv(2, n)
            int inv_2 = (n+1) >> 1;
            while (t > 0){
                if ((t & 1) == 1){
                    // U, V of n+1
                    U, V = ((U + V) * inv_2) % n, ((D*U + V) * inv_2) % n;
                    q = (q * Q) % n;
                    t -= 1;
                }
                else{
                    // U, V of n*2
                    U, V = (U * V) % n, (V * V - 2 * q) % n;
                    q = (q * q) % n;
                    t >>= 1;
                }
            }
            // double s until we have the 2**r*sth Lucas number
            while (r > 0){
                U, V = (U * V) % n, (V * V - 2 * q) % n;
                q = (q * q) % n;
                r -= 1;
            }
            // primality check
            // if n is prime, n divides the n+1st Lucas number, given the assumptions
            return U == 0;
        }
        int legendre(int a, int m){
            return (int)pow(double(a), double((m-1) >> 1)) % m;
        }
        bool is_sprp(long n, int b=2){
            int d = n-1;
            int s = 0;
            while ((d & 1) == 0){
                s ++;
                d >>= 1;
            }
            int x = (int)pow(double(b), double(d)) % d;
            if (x == 1 or x == n-1){
                return true;
            }
            cout << s << endl;
            for (int r=1; r<s; r++){
                x = (x * x) % n;
                if (x == 1){
                    return false;
                }
                else if (x == n-1){
                    return true;
                }
            }  
            return false;
        }
};

extern "C" {
    PrimalityTests* PrimalityTests_new(){ return new PrimalityTests(); }
    bool PrimalityTests_is_prime(PrimalityTests* primalityTests, long n){ primalityTests->is_prime(n); }
}