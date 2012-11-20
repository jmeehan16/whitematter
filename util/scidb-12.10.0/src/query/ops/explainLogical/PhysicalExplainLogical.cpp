/*
**
* BEGIN_COPYRIGHT
*
* This file is part of SciDB.
* Copyright (C) 2008-2012 SciDB, Inc.
*
* SciDB is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation version 3 of the License.
*
* SciDB is distributed "AS-IS" AND WITHOUT ANY WARRANTY OF ANY KIND,
* INCLUDING ANY IMPLIED WARRANTY OF MERCHANTABILITY,
* NON-INFRINGEMENT, OR FITNESS FOR A PARTICULAR PURPOSE. See
* the GNU General Public License for the complete license terms.
*
* You should have received a copy of the GNU General Public License
* along with SciDB.  If not, see <http://www.gnu.org/licenses/>.
*
* END_COPYRIGHT
*/

/*
 * @file LogicalExplainPhysical.cpp
 *
 * @author poliocough@gmail.com
 *
 * explain_logical operator / Physical implementation.
 */

#include <string.h>

#include "query/Operator.h"
#include "query/OperatorLibrary.h"
#include "array/TupleArray.h"
#include "query/QueryProcessor.h"
#include "query/optimizer/Optimizer.h"
#include "SciDBAPI.h"

using namespace std;
using namespace boost;

namespace scidb
{

class PhysicalExplainLogical: public PhysicalOperator
{
public:
    PhysicalExplainLogical(const string& logicalName, const string& physicalName, const Parameters& parameters, const ArrayDesc& schema):
        PhysicalOperator(logicalName, physicalName, parameters, schema)
    {
        _result = boost::shared_ptr<Array>(new TupleArray(_schema, vector<boost::shared_ptr<Tuple> >()));
    }

    virtual ArrayDistribution getOutputDistribution(const std::vector<ArrayDistribution> & inputDistributions,
                                                 const std::vector< ArrayDesc> & inputSchemas) const
    {
        return ArrayDistribution(psLocalInstance);
    }

    void preSingleExecute(boost::shared_ptr<Query> query)
    {
        bool afl = false;

        assert (_parameters.size()==1 || _parameters.size()==2);
        string queryString = ((boost::shared_ptr<OperatorParamPhysicalExpression>&)_parameters[0])->getExpression()->evaluate().getString();

        if (_parameters.size() == 2)
        {
            string languageSpec = ((boost::shared_ptr<OperatorParamPhysicalExpression>&)_parameters[1])->getExpression()->evaluate().getString();
            afl = languageSpec == "afl";
        }

        boost::shared_ptr<QueryProcessor> queryProcessor = QueryProcessor::create();
        boost::shared_ptr<Query> innerQuery = Query::createDetached();
        innerQuery->init(INVALID_QUERY_ID-1,
                         query->mapLogicalToPhysical(query->getCoordinatorID()),
                         query->mapLogicalToPhysical(query->getInstanceID()),
                         query->getCoordinatorLiveness());
        innerQuery->queryString = queryString;

        queryProcessor->parseLogical(innerQuery, afl);
        queryProcessor->inferTypes(innerQuery);

        std::ostringstream planString;
        innerQuery->logicalPlan->toString(planString);

        vector< boost::shared_ptr<Tuple> > tuples(1);
        Tuple& tuple = *new Tuple(1);
        tuples[0] = boost::shared_ptr<Tuple>(&tuple);
        tuple[0].setData(planString.str().c_str(), planString.str().length() + 1);

        _result = boost::shared_ptr<Array>(new TupleArray(_schema, tuples));
    }

    boost::shared_ptr<Array> execute(vector< boost::shared_ptr<Array> >& inputArrays, boost::shared_ptr<Query> query)
    {
        return _result;
    }

private:
    boost::shared_ptr<Array> _result;
};

DECLARE_PHYSICAL_OPERATOR_FACTORY(PhysicalExplainLogical, "explain_logical", "physicalExplainLogical")

} //namespace
