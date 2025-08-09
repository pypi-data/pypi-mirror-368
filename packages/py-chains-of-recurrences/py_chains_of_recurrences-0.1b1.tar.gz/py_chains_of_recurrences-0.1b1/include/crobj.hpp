#pragma once
#include <vector>
#include <algorithm>
#include <cmath>
#include <iostream>
#include <memory>

class CRsum;
class CRnum;
class CRprod;
class CRtrig;
class CRexpr;

inline double choose (double n, double k){ 
    double result = 1;
    for (size_t i = 1; i <= k; i++){ 
        result *= (n-k+i)/i;
    }
    return result;
}

inline size_t fact(size_t n){ 
    size_t result =1; 
    for (size_t i = 1; i<= n; i++){
        result *= i; 
    }
    return result;
}

enum class oc {
    ADD,
    MUL,
    POW,
    EXP,
    LN,
    SIN,
    COS,
    TAN, 
    COT
};

class CRobj {
    public:
        CRobj(){}; 
        CRobj(size_t l);
        virtual ~CRobj() =default ;

        virtual std::unique_ptr<CRobj> add(const CRobj& t) const = 0;
        virtual std::unique_ptr<CRobj> mul(const CRobj& t) const= 0;
        virtual std::unique_ptr<CRobj> pow(const CRobj& t) const= 0;

        virtual std::unique_ptr<CRobj> exp() const= 0;
        virtual std::unique_ptr<CRobj> ln() const= 0;
        virtual std::unique_ptr<CRobj> sin()  const= 0;
        virtual std::unique_ptr<CRobj> cos() const = 0;

        virtual void simplify();
        virtual std::unique_ptr<CRobj> copy() const = 0;

        virtual double initialize();
        virtual double valueof() const;
        virtual bool isnumber() const;
        
        virtual void print_tree() const = 0;

        virtual void shift(size_t index);
    
        std::vector<std::unique_ptr<CRobj>> operands;

        virtual std::string genCode(size_t parent, size_t index, ssize_t place, std::string indent) const = 0;
        std::string prepare( CRobj& root);

        std::vector<double> fastvalues;
        std::vector<double> isanumber;
        std::vector<bool> isnumbers;

        size_t length;
        bool initialized = false;
        size_t crcount = 0;
        ssize_t crposition;
        ssize_t index;

        std::string crprefix = "A";
};
